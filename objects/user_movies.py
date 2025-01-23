from utils import database


class UserMovies:
    def __init__(self, movie_id, title, user_id, poster_path):
        self.movie_id = movie_id
        self.title = title
        self.user_id = user_id
        self.poster_path = poster_path

    @classmethod
    def create_in_database(cls, movie_id, title, user_id, poster_path):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO movies "
                    "(movie_id, title, user_id, poster_path) "
                    "VALUES (%(movie_id)s, %(title)s, %(user_id)s, %(poster_path)s); "
                ),
                (
                    {"movie_id": movie_id, "title": title, "user_id": user_id, "poster_path": poster_path}
                )
                )

        instance = cls(
            movie_id=movie_id,
            title=title,
            user_id=user_id,
            poster_path=poster_path
        )
        return instance

    @classmethod
    def from_id(cls, movie_id):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM movie_id "
                    "WHERE movie_id = %(movie_id)s;"
                ),
                ({"movie_id": movie_id})
            )
            answer = cursor.fetchone()

        if answer is None:
            instance = None
        else:
            instance = cls(
                movie_id=answer.movie_id,
                title=answer.title,
                user_id=answer.user_id,
                poster_path=answer.poster_path
            )

        return instance

