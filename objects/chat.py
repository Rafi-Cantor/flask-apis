from utils import database
import pendulum
import uuid


class ShareCodeDoesntExist(Exception):
    pass


class Chat:

    def __init__(
            self,
            chat_id: uuid.UUID,
            title: str,
            share_code: uuid.UUID,
            created_at: pendulum.DateTime,
            created_by: uuid.UUID
    ):
        self.chat_id = chat_id
        self.title = title
        self.share_code = share_code
        self.created_at = created_at
        self.created_by = created_by

    @classmethod
    def create(cls, title: str, user_id: uuid.UUID):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO chats "
                    "(title, created_by) "
                    "VALUES (%(title)s, %(user_id)s) "
                    "RETURNING *;"
                ),
                {
                    "title": title,
                    "user_id": user_id
                }
            )
            row = cursor.fetchone()

        return cls(
            chat_id=row.chat_id,
            title=row.title,
            share_code=row.share_code,
            created_at=row.created_at,
            created_by=row.created_by
        )

    @classmethod
    def get_by_share_code(cls, share_code: uuid.UUID) -> "Chat":
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT chat_id, share_code, created_at "
                "FROM chats "
                "WHERE share_code = %(share_code)s;",
                {"share_code": share_code},
            )
            row = cursor.fetchone()

        if not row:
            raise ShareCodeDoesntExist(f"Share code {share_code} doesn't exist. ")

        return cls(
            chat_id=row.chat_id,
            title=row.title,
            share_code=row.share_code,
            created_at=row.created_at,
            created_by=row.created_by
        )

    def delete(self) -> None:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "DELETE FROM chats "
                "WHERE chat_id = %(chat_id)s;",
                {
                    "chat_id": self.chat_id,
                },
            )
