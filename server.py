import json
from flask import Flask, jsonify, request, abort, Response

from services import movie_service
from settings import SERVER_HOST, SERVER_PORT, DEBUG


app = Flask(__name__)

ERROR_INVALID_SORT_FIELD = json.dumps({"sort": ["id", "title", "imdb_rating"]})
ERROR_INVALID_SORT_ORDER = json.dumps({"sort_order": ["asc", "desc"]})
ERROR_INVALID_FIELD = "Invalid input"


@app.route("/api/v1/movies", methods=["GET"], strict_slashes=False)
def movies_list() -> str:
    try:
        limit = int(request.args.get("limit", 50))
        page = int(request.args.get("page", 1))
    except ValueError:
        abort(Response(status=422, response=ERROR_INVALID_FIELD))
    if page < 1 or limit < 0:
        abort(Response(status=422, response=ERROR_INVALID_FIELD))
    sort = request.args.get("sort", "id")
    if sort not in ("id", "title", "imdb_rating"):
        abort(Response(status=422, response=ERROR_INVALID_SORT_FIELD))
    sort_order = request.args.get("sort_order", "asc")
    if sort_order not in ("asc", "desc"):
        abort(Response(status=422, response=ERROR_INVALID_SORT_ORDER))
    search = request.args.get("search", "")
    result = movie_service.get_multi(
        page=page, limit=limit, sort=sort, sort_order=sort_order, search=search
    )
    if result is None:
        abort(404)
    return jsonify(result)


@app.route("/api/v1/movies/<movie_id>", methods=["GET"], strict_slashes=False)
def movies_detail(movie_id: str) -> str:
    result = movie_service.get(id=movie_id)
    if result is None:
        abort(404)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
