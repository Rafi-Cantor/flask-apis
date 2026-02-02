from utils import database
import pendulum
import uuid
from chat import Chat
from user import User


class UserChatMappingDoesntExist(Exception):
    pass


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

    @staticmethod
    def check_exists(user_id: uuid.UUID, chat_id: uuid.UUID):
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT user_id, chat_id,  joined_at"
                "FROM user_chat_mappings "
                "WHERE user_id=%(user_id)s and chat_id=%(chat_id)s;",
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                },
            )
            mapping = cursor.fetchone()

        if not mapping:
            raise UserChatMappingDoesntExist(f"No user chat mapping exists for user: {user_id} - chat: {user_id} ")

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
    def get_chats_for_user(cls, user_id: uuid.UUID) -> list["Chat"]:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT c.chat_id, c.title, c.share_code, c.created_at, ucm.joined_at "
                "FROM chats c "
                "JOIN user_chat_mappings ucm ON c.chat_id = ucm.chat_id "
                "WHERE ucm.user_id = %(user_id)s;",
                {"user_id": user_id},
            )

            rows = cursor.fetchall()

        if len(rows) == 0:
            raise UserChatMappingDoesntExist(f"No user chat mapping exists for user {user_id}")

        return [
            Chat(
                chat_id=row.chat_id,
                share_code=row.share_code,
                title=row.title,
                created_at=row.created_at,
            )
            for row in rows
        ]

    @classmethod
    def get_users_for_chat(cls, chat_id: uuid.UUID) -> list["User"]:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT u.user_id, u.name, u.email "
                "FROM users u "
                "JOIN user_chat_mappings ucm ON u.user_id = ucm.user_id "
                "WHERE ucm.chat_id = %(chat_id)s;",
                {"chat_id": chat_id},
            )

            rows = cursor.fetchall()

        if len(rows) == 0:
            raise UserChatMappingDoesntExist(f"No user chat mapping exists for chat {chat_id}")

        return [
            User(
                user_id=row.user_id,
                email=row.email,
                cognito_id=row.cognito_id,
                avatar_url=row.avatar_url,
                email_verified=row.email_verified
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
