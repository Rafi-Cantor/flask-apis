from utils import database
import pendulum
import uuid


class Chat:

    def __init__(self, chat_id: uuid.UUID, share_code: uuid.UUID, created_at: pendulum.DateTime):
        self.chat_id = chat_id
        self.share_code = share_code
        self.created_at = created_at

    @staticmethod
    def create(chat_id: uuid.UUID, share_code: uuid.UUID, created_at: pendulum.DateTime):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO chats "
                    "(chat_id, share_code, created_at) "
                    "VALUES (%(chat_id)s, %(share_code)s, %(created_at)s); "
                ),
                {
                    "chat_id": chat_id,
                    "share_code": share_code,
                    "created_at": created_at
                }
            )

    @staticmethod
    def delete(chat_id: uuid.UUID) -> None:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "DELETE FROM chat "
                "WHERE chat_id = %(chat_id)s;",
                {
                    "chat_id": chat_id,
                },
            )











