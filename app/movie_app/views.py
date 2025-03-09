from app.auth.views import multi_auth
from flask import request, jsonify
from app.movie_app import movie_app
from objects import user_movies
from integrations import the_movie_db


@movie_app.route("/movies_by_page_number", methods=["GET"])
@multi_auth.login_required
def discover_movies():
    data = request.get_json()
    page_number = data.get('page_number')
    if not page_number:
        return jsonify({}), 400
    u = multi_auth.current_user()
    watched_movie_ids = [movie.movie_id for movie in user_movies.UserMovies.from_user_id(u.user_id)]
    client = the_movie_db.TMDBClient()
    discover_endpoint = the_movie_db.TMDBMovieDiscovery(page=page_number)
    discover_api = the_movie_db.TMDBMovieAPI(client, discover_endpoint)
    response = discover_api.fetch()
    results_list = response.json()["results"]
    results = [
        {
            "id": movie['id'],
            "title": movie["title"],
            "release_date": movie["release_date"],
            "poster_path": movie["poster_path"],
            "watched": movie["id"] in watched_movie_ids
        } for movie in results_list
    ]

    return jsonify({"results": results})


@movie_app.route("/search_movies", methods=["GET"])
@multi_auth.login_required
def search_movies():
    data = request.get_json()
