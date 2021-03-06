import aiohttp.web
from os import getenv
import aiohttp_cors

import app.UserController as User
from app.AuthenticateController import authenticate
import app.SummaryController as Summary
import app.HistoryController as History
from app.db.startup import on_startup as db_on_startup
from app.db.cleanup import on_cleanup as db_on_cleanup

async def index(_: aiohttp.web.Request) -> aiohttp.web.Response:
  return aiohttp.web.Response(
    text="Welcome to Tidbit Backend API",
    status=200
  )

app = aiohttp.web.Application()

app.router.add_get(path="/", handler=index)
app.router.add_post(path="/user", handler=User.create)
app.router.add_get(path="/user/{user_id}", handler=User.get)
app.router.add_post(path="/user/{user_id}", handler=User.update)
app.router.add_delete(path="/user/{user_id}", handler=User.delete)
app.router.add_post(path="/authenticate", handler=authenticate)
app.router.add_post(path="/summary", handler=Summary.summarize)
app.router.add_get(path="/summary/types", handler=Summary.get_summarizer_types)
app.router.add_get(path="/user/{user_id}/history", handler=History.index)

cors = aiohttp_cors.setup(app, defaults={
  "*": aiohttp_cors.ResourceOptions(
    allow_credentials=True,
    expose_headers="*",
    allow_headers="*",
  )
})
for route in list(app.router.routes()):
    cors.add(route)

app.on_startup.append(db_on_startup)
app.on_cleanup.append(db_on_cleanup)

aiohttp.web.run_app(
  app,
  port=int(getenv('BACKEND_PORT', '80'))
)
