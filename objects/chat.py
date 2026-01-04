from utils import database
import pendulum
import uuid


class Chat:

    def __init__(self, chat_id: uuid.UUID, title: str, share_code: uuid.UUID, created_at: pendulum.DateTime):
        self.chat_id = chat_id
        self.title = title
        self.share_code = share_code
        self.created_at = created_at

    @staticmethod
    def create(share_code: uuid.UUID, created_at: pendulum.DateTime):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO chats "
                    "(share_code, created_at) "
                    "VALUES (%(chat_id)s, %(share_code)s, %(created_at)s); "
                ),
                {
                    "share_code": share_code,
                    "created_at": created_at
                }
            )

    @classmethod
    def get_by_share_code(cls, share_code: uuid.UUID) -> "Chat | None":
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT chat_id, share_code, created_at "
                "FROM chats "
                "WHERE share_code = %(share_code)s;",
                {"share_code": share_code},
            )
            row = cursor.fetchone()

        if not row:
            return None

        return cls(
            chat_id=row.chat_id,
            title=row.title,
            share_code=row.share_code,
            created_at=row.created_at,
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
