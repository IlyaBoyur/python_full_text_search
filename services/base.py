import logging
import requests
from abc import ABC, abstractmethod
from typing import Any


logger = logging.getLogger(__name__)


class Repository(ABC):
    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_multi(self, *args, **kwargs):
        pass


class RepositoryES(Repository):
    def __init__(self, url: str) -> None:
        self._url = url

    def get(self, index: str, id: Any, fields: list[str] | None = None) -> dict | None:
        params = {"_source": ",".join(fields)} if fields else {}
        try:
            response = requests.get(f"{self._url}/{index}/_doc/{id}", params=params)
            data = response.json()
        except requests.RequestException as error:
            logger.error(error)
            return
        if not data["found"]:
            return
        return {"id": data["_id"], **data["_source"]}

    def get_multi(
        self,
        index: str,
        *,
        fields: list[str] | None = None,
        filter: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_field: str = "id",
        sort_order: str = "asc",
        query: dict[str, Any] | None = None,
    ) -> list[dict] | None:
        params = {"_source": ",".join(fields)} if fields else {}
        data = {"from": skip, "size": limit}
        if sort_field and sort_order:
            data["sort"] = [{sort_field: {"order": sort_order}}]
        if query:
            data["query"] = query
        filter = filter or {}
        print(f"params: {params}")
        print(f"data: {data}")
        try:
            response = requests.get(
                f"{self._url}/{index}/_search", params=params, json=data
            )
            data = response.json()
        except requests.RequestException as error:
            logger.error(error)
            return
        return [doc["_source"] for doc in data["hits"]["hits"]]
