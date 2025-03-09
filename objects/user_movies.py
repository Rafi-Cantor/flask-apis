from utils import database


class UserMovies:
    def __init__(self, movie_id, title, user_id, poster_path):
        self.movie_id = movie_id
        self.user_id = user_id
        self.title = title
        self.poster_path = poster_path

    @classmethod
    def create_in_database(cls, movie_id, user_id,title, poster_path):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO user_movies "
                    "(movie_id, user_id, title, poster_path) "
                    "VALUES (%(movie_id)s, %(user_id)s, %(title)s, , %(poster_path)s); "
                ),
                (
                    {"movie_id": movie_id, "title": title, "user_id": user_id, "poster_path": poster_path}
                )
                )

        instance = cls(
            movie_id=movie_id,
            user_id=user_id,
            title=title,
            poster_path=poster_path
        )
        return instance

    @classmethod
    def from_user_id(cls, user_id):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM user_movies "
                    "WHERE user_id = %(user_id)s;"
                ),
                ({"user_id": user_id})
            )
            answers = cursor.fetchall()
        user_movies = [
            cls(
                movie_id=a.movie_id,
                user_id=a.user_id,
                title=a.title,
                poster_path=a.poster_path
            ) for a in answers
        ]
        return user_movies
