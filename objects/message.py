from utils import database
import pendulum
import uuid


class Message:

    def __init__(
            self,
            message_id: uuid.UUID,
            chat_id: uuid.UUID,
            content: str,
            sent_by: int,
            created_at: pendulum.DateTime
    ):
        self.message_id = message_id
        self.chat_id = chat_id
        self.content = content
        self.sent_by = sent_by
        self.created_at = created_at

    def __repr__(self):
        return f"<Message id={self.message_id} chat id={self.chat_id} content={self.content} " \
               f"sent by={self.sent_by} created at={self.created_at}>"

    @staticmethod
    def create(chat_id: uuid.UUID, content: str, sent_by: int, created_at: pendulum.DateTime):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO messages "
                    "(chat_id, content, sent_by, created_at) "
                    "VALUES (%(chat_id)s, %(content)s, %(sent_by)s, %(created_at)s); "
                ),
                    {
                        "chat_id": chat_id,
                        "content": content,
                        "sent_by": sent_by,
                        "created_at": created_at
                    }
            )
