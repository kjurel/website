import functools
import logging
import os
import shutil
from typing import TextIO

import requests
from tortoise import Tortoise

from .prefs import settings


class TrashManager:
    folder: str = "temp"

    def __init__(self) -> None:
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    def close(self):
        shutil.rmtree(self.folder, True)

    def flush(self):
        for filename in os.listdir(self.folder):
            file_path = os.path.join(self.folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

    def save(self, byts: bytes, filename: str):
        fpath = os.path.join(self.folder, filename)
        with open(fpath, "wb") as f:
            f.write(byts)
        return fpath


async def complete_reset(url: str):
    DATABASE_URL = url
    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": settings.get_db_app_list()}
    )
    await reset_tortoise("public", True)
    await Tortoise.close_connections()


async def reset_tortoise(schema: str, delete_all: bool):
    conn = Tortoise.get_connection("default")

    TABLES = (
        "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{}'"
        " AND TABLE_TYPE='BASE TABLE';"
    )
    EXISTS = (
        "SELECT EXISTS(SELECT FROM INFORMATION_SCHEMA.TABLES"
        " WHERE TABLE_SCHEMA='{}' AND TABLE_NAME='{}');"
    )
    DELETE = "DROP TABLE {}.{} CASCADE;"

    tables_in_database = [
        record["table_name"]
        for record in (await conn.execute_query(TABLES.format(schema)))[1]
    ]

    if delete_all:
        tables_to_delete = tables_in_database
    else:
        tables_to_delete = [
            tablename
            for k, v in Tortoise.apps["models"].items()
            if (tablename := v.Meta.__dict__.get("table", None) or k)
            in tables_in_database
        ]

    await conn.execute_script(
        " ".join([DELETE.format(schema, f'"{name}"') for name in tables_to_delete])
    )

    if any(
        [
            (await conn.execute_query(EXISTS.format(schema, name)))[1][0]["exists"]
            for name in tables_to_delete
        ]
    ):
        raise Exception("tables were not deleted")


def partialclass(cls, *args, **kwds):
    class NewCls(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwds)

    return NewCls


def generateWebhook(console_log: bool, webhook_log: bool) -> logging.StreamHandler:
    class WebhookStream(logging.StreamHandler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                msg = self.format(record)
                stream: TextIO = self.stream
                if console_log:
                    stream.write(msg + self.terminator)
                if webhook_log:
                    requests.post(os.environ["WBHK_URL"], json={"content": msg})
                self.flush()
            except Exception:
                self.handleError(record)

    format_string = "`%(name)s : %(levelname)s - %(message)s`"
    handler = WebhookStream()
    handler.setFormatter(logging.Formatter(format_string))
    return handler
