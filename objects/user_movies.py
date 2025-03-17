from utils import database
import psycopg2


class UserMovies:
    def __init__(self, record_id: int, movie_id: int, title: str, user_id: int, poster_path: str):
        self.record_id = record_id
        self.movie_id = movie_id
        self.user_id = user_id
        self.title = title
        self.poster_path = poster_path

    @classmethod
    def create_in_database(cls, movie_id: int, user_id: int, title: str, poster_path: str):
        try:
            with database.cursor_scope() as cursor:
                cursor.execute(
                    (
                        "INSERT INTO user_movies "
                        "(movie_id, user_id, title, poster_path) "
                        "VALUES (%(movie_id)s, %(user_id)s, %(title)s, %(poster_path)s); "
                    ),
                    (
                        {"movie_id": movie_id, "title": title, "user_id": user_id, "poster_path": poster_path}
                    )
                    )
        except psycopg2.DatabaseError:
            raise

    @classmethod
    def from_user_id(cls, user_id: int):
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
                record_id=a.record_id,
                movie_id=a.movie_id,
                user_id=a.user_id,
                title=a.title,
                poster_path=a.poster_path
            ) for a in answers
        ]
        return user_movies

    @classmethod
    def from_user_id_and_movie_id(cls, movie_id: int, user_id: int):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM user_movies "
                    "WHERE user_id = %(user_id)s AND movie_id = %(movie_id)s;"
                ),
                ({"user_id": user_id, "movie_id": movie_id})
            )
            answer = cursor.fetchone()
        if answer is None:
            return None
        return cls(
                record_id=answer.record_id,
                movie_id=answer.movie_id,
                user_id=answer.user_id,
                title=answer.title,
                poster_path=answer.poster_path
            )

    @staticmethod
    def delete_from_database(record_id: int):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "DELETE FROM user_movies "
                    "WHERE record_id = %(record_id)s;"
                ),
                ({"record_id": record_id})
            )
