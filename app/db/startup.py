from aiohttp.web import Application
import aiopg
from os import getenv
from asyncio import sleep
from .UserRepository import UserRepository
from .HistoryRepository import HistoryRepository
from .DocumentRepository import DocumentRepository

async def on_startup(app: Application):

  db_name = getenv('POSTGRES_DB_NAME')
  db_username = getenv('POSTGRES_DB_USERNAME')
  db_password = getenv('POSTGRES_DB_PASSWORD')
  db_host = getenv('POSTGRES_DB_HOST')

  if not (db_name and db_username and db_password and db_host):
    raise RuntimeError('DB environment variables not set!')

  await sleep(10)

  dsn = 'dbname={} user={} password={} host={}'.format(
    getenv('POSTGRES_DB_NAME'),
    getenv('POSTGRES_DB_USERNAME'),
    getenv('POSTGRES_DB_PASSWORD'),
    getenv('POSTGRES_DB_HOST')
  )
  db_pool = await aiopg.create_pool(
    dsn=dsn,
    loop=app.loop
  )

  await UserRepository(db_pool).startup()
  await DocumentRepository(db_pool).startup()
  await HistoryRepository(db_pool).startup()

  app['db_pool'] = db_pool
