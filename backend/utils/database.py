from app.settings.config import settings
from tortoise import Tortoise


async def complete_reset(url: str):
  DATABASE_URL = url
  await Tortoise.init(
      db_url=DATABASE_URL,
      modules={ "models": settings.get_db_app_list() }
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
        tablename for k,
        v in Tortoise.apps["models"].items()
        if (tablename := v.Meta.__dict__.get("table",
                                             None) or k) in tables_in_database
    ]
  
  await conn.execute_script(
      " ".join(
          [DELETE.format(schema,
                         f'"{name}"') for name in tables_to_delete]
      )
  )
  
  if any(
      [
          (await conn.execute_query(EXISTS.format(schema,
                                                  name)))[1][0]["exists"]
          for name in tables_to_delete
      ]
  ):
    raise Exception("tables were not deleted")
