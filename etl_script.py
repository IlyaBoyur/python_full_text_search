import contextlib
import json
import logging
import os
import sqlite3
from dataclasses import dataclass, asdict
from typing import Any
from dotenv import load_dotenv

import requests

load_dotenv()


DB_NAME = os.environ.get("DB_NAME", "db.sqlite")
BULK_SIZE = int(os.environ.get("BULK_SIZE", "1"))

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
ES_INDEX_NAME = os.environ.get("ES_INDEX_NAME", "movies")


logger = logging.getLogger(__name__)


@dataclass
class FilmWorkSQL:
    id: str
    title: str
    description: str
    rating: float


@dataclass
class PersonSQL:
    id: str
    full_name: str


@dataclass
class PersonES:
    id: str
    name: str


@dataclass
class Actor(PersonES):
    ...


@dataclass
class Director(PersonES):
    ...


@dataclass
class Writer(PersonES):
    ...


@dataclass
class FilmES:
    id: str
    title: str
    description: str
    imdb_rating: float
    genres: str
    actors_names: str
    directors_names: str
    writers_names: str
    actors: list[dict]
    directors: list[dict]
    writers: list[dict]


# def retry_block(func, *args, **kwargs):
#     retries = 3
#     ok = False
#     while (retries and not ok):
#         try:
#             result = func(*args, **kwargs)
#             ok = True
#         except Exception:
#             retries -= 1
#             logger.warning(f"Retry attempts left: {retries}")
#     if not ok:
#         raise Exception
#     return result


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def _extract_film_genres(self, films: list[str]) -> dict[str, list[str]]:
        data = self.connection.execute(
            """SELECT fw.id, GROUP_CONCAT(g.name, ',')
            FROM genre g
            JOIN genre_film_work gfw on g.id == gfw.genre_id
            JOIN film_work fw on gfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """)
            GROUP BY fw.id;""",
            films,
        ).fetchall()
        return {id_: genres.split(",") for id_, genres in data}

    def _extract_film_persons(self, films: list[str]) -> dict[str, str]:
        data = self.connection.execute(
            """SELECT p.id, p.full_name
            FROM person p
            JOIN person_film_work pfw on p.id == pfw.person_id
            JOIN film_work fw on pfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """);""",
            films,
        ).fetchall()
        return {id_: PersonSQL(id_, *record) for id_, *record in data}

    def _extract_film_persons_by_role(
        self, films: list[str], role: str
    ) -> dict[str, list[str]]:
        data = self.connection.execute(
            """SELECT fw.id, GROUP_CONCAT(p.id, ',')
            FROM person p
            JOIN person_film_work pfw on p.id == pfw.person_id
            JOIN film_work fw on pfw.film_work_id == fw.id
            WHERE fw.id in ("""
            + ", ".join("?" for _ in films)
            + """) and pfw.role == ?
            GROUP BY fw.id;""",
            (*films, role),
        ).fetchall()
        return {id_: person_ids.split(",") for id_, person_ids in data}

    # @retry_block()
    def _extract_film_data(self, film_ids: list[str]) -> dict:
        result = {
            "genres": self._extract_film_genres(film_ids),
            "persons": self._extract_film_persons(film_ids),
            "film_actors": self._extract_film_persons_by_role(film_ids, "actor"),
            "film_directors": self._extract_film_persons_by_role(film_ids, "director"),
            "film_writers": self._extract_film_persons_by_role(film_ids, "writer"),
        }
        return result

    def bulk_generator(self, bulk_size: int | None = None):
        with self.connection as cursor:
            film_cursor = cursor.execute(
                "SELECT id, title, description, rating FROM film_work;"
            )
            test = 0
            while True:
                if test > 0:
                    break
                bulk = film_cursor.fetchmany(size=bulk_size or cursor.arraysize)
                if bulk:
                    films = [FilmWorkSQL(*record) for record in bulk]
                    result = {
                        "films": films,
                        **self._extract_film_data([film.id for film in films]),
                    }
                    logger.info("DATA FETCHED: %s", result)
                    yield result
                    test += 1
                else:
                    break


class SQLite2ESTransformer:
    def transform(self, data: dict[str, Any]) -> list:
        transformed = []
        for film in data["films"]:
            persons = data["persons"]
            actors = [
                Actor(id=id_, name=persons[id_].full_name)
                for id_ in data["film_actors"][film.id]
            ]
            directors = [
                Director(id=id_, name=persons[id_].full_name)
                for id_ in data["film_directors"][film.id]
            ]
            writers = [
                Writer(id=id_, name=persons[id_].full_name)
                for id_ in data["film_writers"][film.id]
            ]
            transformed.append(
                FilmES(
                    id=film.id,
                    title=film.title,
                    description=film.description,
                    imdb_rating=film.rating,
                    genres=",".join(genre for genre in data["genres"][film.id]),
                    actors_names=",".join(actor.name for actor in actors),
                    directors_names=",".join(director.name for director in directors),
                    writers_names=",".join(writer.name for writer in writers),
                    actors=[asdict(actor) for actor in actors],
                    directors=[asdict(director) for director in directors],
                    writers=[asdict(writer) for writer in writers],
                )
            )
        logger.info("DATA TRANSFORMED: %s", "\n".join(str(el) for el in transformed))
        return transformed


class ESLoader:
    def __init__(self, url="", index=""):
        self.url = url
        self.index = index
        self._loaded = set()

    def _prepare_bulk_query(self, data: list[FilmES]) -> str:
        """
        {"index": {"_index": "movies", "_id": "my_id"}}
        {"field1": "1", "field2": "2"}
        {"index": {"_index": "movies", "_id": "my_id2"}}
        {"field1": "3", "field2": "4"}
        """
        return (
            "\n".join(
                json.dumps({"index": {"_index": self.index, "_id": record.id}})
                + "\n"
                + json.dumps(asdict(record))
                for record in data
            )
            + "\n"
        )

    @property
    def loaded(self):
        return self._loaded

    def update_loaded(self, data):
        self._loaded.add(data)

    def bulk_load(self, data: list[FilmES]):
        # logger.info("DATA LOADED: not yet")
        # return
        payload = self._prepare_bulk_query(data)
        logger.info("DATA BEFORE LOADING: %s", payload)
        try:
            response = requests.post(
                f"{self.url}/_bulk",
                data=payload,
                headers={"Content-Type": "application/x-ndjson"},
            )
            print(response.json())
        except requests.RequestException as error:
            logger.error("Connection with ES failed")
            raise RuntimeError(error)

        json_response = json.loads(response.content.decode())
        for item in json_response["items"]:
            if error_message := item["index"].get("error"):
                logger.error(error_message)

        logger.info(
            "DATA LOADED: %s",
            [
                item["index"]["_id"]
                for item in json_response["items"]
                if item["index"]["status"] == 200
            ],
        )


class ETL:
    def __init__(self, extractor, transformer, loader) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def bulk_generator(self, bulk_size):
        yield from self.extractor.bulk_generator(bulk_size=bulk_size)

    def transform(self, data):
        return self.transformer.transform(data=data)

    def bulk_load(self, data):
        return self.loader.bulk_load(data=data)

    def do(self):
        for bulk in self.bulk_generator(bulk_size=BULK_SIZE):
            self.bulk_load(self.transform(bulk))


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] - %(asctime)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
    )
    with contextlib.closing(sqlite3.connect(DB_NAME)) as connection:
        ETL(
            SQLiteExtractor(connection=connection),
            SQLite2ESTransformer(),
            ESLoader(url=ES_URL, index=ES_INDEX_NAME),
        ).do()
