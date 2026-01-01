from utils import database
import pendulum
import uuid


class UserChatMapping:
    def __init__(
        self,
        user_id: uuid.UUID,
        chat_id: uuid.UUID,
        joined_at: pendulum.DateTime,
    ):
        self.user_id = user_id
        self.chat_id = chat_id
        self.joined_at = joined_at

    def __repr__(self):
        return (
            f"<UserChatMapping user_id={self.user_id} "
            f"chat_id={self.chat_id} joined_at={self.joined_at}>"
        )

    @classmethod
    def create(cls, user_id: uuid.UUID, chat_id: uuid.UUID) -> "UserChatMapping":
        with database.cursor_scope() as cursor:
            cursor.execute(
                "INSERT INTO user_chat_mappings (user_id, chat_id) "
                "VALUES (%(user_id)s, %(chat_id)s) "
                "RETURNING user_id, chat_id, joined_at;",
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                },
            )

            row = cursor.fetchone()

        return cls(
            user_id=row.user_id,
            chat_id=row.chat_id,
            joined_at=row.joined_at,
        )

    @classmethod
    def get_chats_for_user(cls, user_id: uuid.UUID) -> list["UserChatMapping"]:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT * "
                "FROM user_chat_mappings "
                "WHERE user_id = %(user_id)s;",
                {"user_id": user_id},
            )

            rows = cursor.fetchall()

        return [
            cls(
                user_id=row.user_id,
                chat_id=row.chat_id,
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    @classmethod
    def get_users_for_chat(cls, chat_id: uuid.UUID) -> list["UserChatMapping"]:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT * "
                "FROM user_chat_mappings "
                "WHERE chat_id = %(chat_id)s;",
                {"chat_id": chat_id},
            )

            rows = cursor.fetchall()

        return [
            cls(
                user_id=row.user_id,
                chat_id=row.chat_id,
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    @staticmethod
    def delete(user_id: uuid.UUID, chat_id: uuid.UUID) -> None:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "DELETE FROM user_chat_mappings "
                "WHERE user_id = %(user_id)s "
                "AND chat_id = %(chat_id)s;",
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                },
            )


