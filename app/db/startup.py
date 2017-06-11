from aiohttp.web import Application
import aiopg
from os import getenv

async def on_startup(app: Application):

  db_name = getenv("DB_NAME")
  db_username = getenv("DB_USERNAME")
  db_password = getenv("DB_PASSWORD")
  db_host = getenv("DB_HOST")

  if not (db_name and db_username and db_password and db_host):
    raise RuntimeError("DB environment variables not set!")

  dsn = 'dbname={} user={} password={} host={}'.format(
    getenv('DB_NAME'),
    getenv('DB_USERNAME'),
    getenv('DB_PASSWORD'),
    getenv('DB_HOST')
  )
  app['db_pool'] = aiopg.create_pool(dsn=dsn)
