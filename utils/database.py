import contextlib
import psycopg2
import settings
import psycopg2.extras as db_extras


@contextlib.contextmanager
def cursor_scope(auto_commit=True, dict_cursor=False):
    con = psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER_NAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_ENDPOINT,
        port=5432,
        sslmode='require'
    )
    if dict_cursor:
        cursor_factory = db_extras.DictCursor
    else:
        cursor_factory = db_extras.NamedTupleCursor
    cursor = con.cursor(cursor_factory=cursor_factory)
    try:
        yield cursor
        if auto_commit:
            con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        cursor.close()
        con.close()
