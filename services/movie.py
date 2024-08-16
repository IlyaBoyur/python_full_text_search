import logging
from dataclasses import dataclass, fields

from settings import ES_URL, ES_INDEX_NAME

from .base import RepositoryES


logger = logging.getLogger(__name__)


@dataclass
class MovieList:
    id: str
    title: str
    imdb_rating: float


@dataclass
class MovieDetail:
    id: str
    title: str
    description: str
    imdb_rating: float
    writers: list[dict]
    actors: list[dict]
    genres: str
    directors: list[dict]


class MovieRepository(RepositoryES):
    def __init__(self, *args, index: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._index = index

    def get(self, id: str) -> dict | None:
        return super().get(
            index=self._index, id=id, fields=tuple(f.name for f in fields(MovieDetail))
        )

    def get_multi(
        self,
        page: int = 1,
        limit: int = 50,
        sort: str = "id",
        sort_order: str = "asc",
        search: str = "",
        **kwargs
    ) -> list[dict] | None:
        """
        page - страница запроса
        limit - число документов на страницу
        """
        skip = (page - 1) * limit
        if search:
            search = {
                "multi_match": {
                    "query": search,
                    "fuzziness": "auto",
                    "fields": [
                        "title^5",
                        "description^4",
                        "genres^3",
                        "actors_names^3",
                        "writers_names^2",
                        "directors_names",
                    ],
                }
            }
        return super().get_multi(
            index=self._index,
            fields=tuple(f.name for f in fields(MovieList)),
            skip=skip,
            limit=limit,
            sort_field=sort,
            sort_order=sort_order,
            query=search,
            **kwargs
        )


movie_service = MovieRepository(url=ES_URL, index=ES_INDEX_NAME)
