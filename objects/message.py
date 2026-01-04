from utils import database
import pendulum
import uuid


class Message:

    def __init__(
            self,
            message_id: uuid.UUID,
            chat_id: uuid.UUID,
            content: str,
            sent_by: uuid.UUID,
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
    def create(chat_id: uuid.UUID, content: str, sent_by: uuid.UUID):
        with database.cursor_scope() as cursor:
            cursor.execute(
                (
                    "INSERT INTO messages "
                    "(chat_id, content, sent_by, created_at) "
                    "VALUES (%(chat_id)s, %(content)s, %(sent_by)s; "
                ),
                {
                    "chat_id": chat_id,
                    "content": content,
                    "sent_by": sent_by,
                }
            )


class Messages:
    @staticmethod
    def get_messages_by_chat_id(chat_id: uuid.UUID, order: str = "ASC") -> list["Message"]:
        with database.cursor_scope() as cursor:
            cursor.execute(
                "SELECT message_id, chat_id, content, sent_by, created_at "
                "FROM messages "
                "WHERE chat_id = %(chat_id)s "
                "ORDER BY created_at %(order)s; ",
                {
                    "chat_id": chat_id,
                    "order": order
                }
            )
            rows = cursor.fetchall()
            return [
                Message(
                    message_id=row["message_id"],
                    chat_id=row["chat_id"],
                    content=row["content"],
                    sent_by=row["sent_by"],
                    created_at=pendulum.parse(str(row["created_at"]))
                )
                for row in rows
            ]
