from aiohttp.web import Application
import aiopg
from os import getenv

async def on_startup(app: Application):

  db_name = getenv('POSTGRES_DB_NAME')
  db_username = getenv('POSTGRES_DB_USERNAME')
  db_password = getenv('POSTGRES_DB_PASSWORD')
  db_host = getenv('POSTGRES_DB_HOST')

  if not (db_name and db_username and db_password and db_host):
    raise RuntimeError('DB environment variables not set!')

  dsn = 'dbname={} user={} password={} host={}'.format(
    getenv('POSTGRES_DB_NAME'),
    getenv('POSTGRES_DB_USERNAME'),
    getenv('POSTGRES_DB_PASSWORD'),
    getenv('POSTGRES_DB_HOST')
  )
  app['db_pool'] = aiopg.create_pool(dsn=dsn)
