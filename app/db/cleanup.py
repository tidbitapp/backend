from aiohttp.web import Application

async def on_cleanup(app: Application):

  db_pool = app['db_pool']

  db_pool.terminate()
  db_pool.wait_closed()

