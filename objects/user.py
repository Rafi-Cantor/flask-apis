from utils import database


class CannotCreateNewUserError(Exception):
    pass


class UserDoesntExistInDatabaseError(Exception):
    pass


class CannotVerifyEmailError(Exception):
    pass


class CannotDeleteUserError(Exception):
    pass


class User:

    def __init__(self, user_id, cognito_id: str, email: str, email_verified: bool = False):
        self.user_id = user_id
        self.cognito_id = cognito_id
        self.email = email
        self.email_verified = email_verified

    @classmethod
    def create(cls, cognito_id: str, email: str, email_verified: bool = False) -> "User":
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO users "
                    "(cognito_id, email, email_verified) "
                    "VALUES (%(cognito_id)s, %(email)s, %(email_verified)s); "
                ),
                (
                    {"cognito_id": cognito_id, "email": email, "email_verified": email_verified}
                )
                )

        instance = cls.from_email(email)

        return instance

    @classmethod
    def from_email(cls, email: str) -> "User":
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "select * from users "
                    "WHERE  email = %(email)s; "
                ),
                ({"email": email})
            )

            answer = cursor.fetchone()

        if answer is None:
            raise Exception(f"No user found in database with {email}. ")
        else:
            instance = cls(
                user_id=answer.user_id,
                cognito_id=answer.cognito_id,
                email=answer.email,
                email_verified=answer.email_verified
            )

        return instance

    @classmethod
    def from_user_id(cls, user_id: str) -> "User":
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "SELECT * FROM users "
                    "WHERE user_id = %(user_id)s;"
                ),
                ({"user_id": user_id})
            )
            answer = cursor.fetchone()

        if answer is None:
            instance = None
        else:
            instance = cls(
                user_id=answer.user_id,
                cognito_id=answer.cognito_id,
                email=answer.user_id,
                email_verified=answer.email_verified
            )

        return instance

    @staticmethod
    def delete(user_id: str):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "DELETE FROM users "
                    "WHERE  user_id = %(user_id)s;"
                ),
                ({"user_id": user_id})
            )

    def verify_email(self, user_id: str):

        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "UPDATE users "
                    "SET email_verified = true "
                    "WHERE user_id = %(user_id)s;"
                ),
                (
                    {"user_id": user_id}
                )
            )

        self.email_verified = True

