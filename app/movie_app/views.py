from app.auth.views import multi_auth
from flask import request, jsonify
from app.movie_app import movie_app
from objects import user_movies
from integrations import the_movie_db


@movie_app.route("/movies_by_page_number/<page_number>", methods=["GET"])
@multi_auth.login_required
def discover_movies(page_number):
    u = multi_auth.current_user()
    watched_movie_ids = [movie.movie_id for movie in user_movies.UserMovies.from_user_id(u.user_id)]
    client = the_movie_db.TMDBClient()
    discover_endpoint = the_movie_db.TMDBMovieDiscovery(page=page_number)
    discover_api = the_movie_db.TMDBMovieAPI(client, discover_endpoint)
    try:
        response = discover_api.fetch()
    except the_movie_db.TMDBAPIError as e:
        return jsonify({'error_message': f'{e}. '}), 500
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
    page_number = data.get('page_number')
    query = data.get('query')
    u = multi_auth.current_user()
    watched_movie_ids = [movie.movie_id for movie in user_movies.UserMovies.from_user_id(u.user_id)]
    client = the_movie_db.TMDBClient()
    search_endpoint = the_movie_db.TMDBMovieSearch(page=page_number, query=query)
    search_api = the_movie_db.TMDBMovieAPI(client, search_endpoint)
    try:
        response = search_api.fetch()
    except the_movie_db.TMDBAPIError as e:
        return jsonify({'error_message': f'{e}. '}), 500
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


@movie_app.route("/add_movie_to_favourites", methods=["POST"])
@multi_auth.login_required
def add_movie_to_favourites():
    data = request.get_json()
    movie_id = data.get('movie_id')
    if not movie_id:
        return jsonify({'error_message': 'movie_id is required. '}), 400
    u = multi_auth.current_user()
    client = the_movie_db.TMDBClient()
    endpoint = the_movie_db.TMDBMovieById(movie_id=movie_id)
    api = the_movie_db.TMDBMovieAPI(client, endpoint)
    try:
        response = api.fetch()
    except the_movie_db.TMDBAPIError as e:
        return jsonify({'error_message': f'{e}.'}), 500

    response_json = response.json()
    poster_path = response_json["poster_path"]
    title = response_json["title"]
    user_movies.UserMovies.create_in_database(
            movie_id=movie_id,
            user_id=u.user_id,
            title=title,
            poster_path=poster_path
        )

    return jsonify({"message": f"Successfully added {title} to favourites"}), 201


@movie_app.route("/delete_movie_from_favourites", methods=["POST"])
@multi_auth.login_required
def delete_movie_from_favourites():
    data = request.get_json()
    movie_id = data.get('movie_id')
    if not movie_id:
        return jsonify({'error_message': 'movie_id is required. '}), 400
    u = multi_auth.current_user()
    deleted_movie = user_movies.UserMovies.from_user_id_and_movie_id(movie_id=movie_id, user_id=u.user_id)
    user_movies.UserMovies.delete_from_database(movie_id=movie_id, user_id=u.user_id)
    return jsonify({"message": f"Successfully deleted {deleted_movie.title} to favourites"}), 201
