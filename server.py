import aiohttp.web
import app.UserController as User
from app.AuthenticateController import authenticate
from app.SummaryController import summarize
from app.db.startup import on_startup as db_on_startup

async def index() -> aiohttp.web.Response:
  return aiohttp.web.Response(
    text="Welcome to Tidbit Backend API",
    status=200
  )

app = aiohttp.web.Application()

app.router.add_route(method="*", path="/", handler=index)
app.router.add_post(path="/user", handler=User.create)
app.router.add_get(path="/user/{user_id}", handler=User.get)
app.router.add_post(path="/user/{user_id}", handler=User.update)
app.router.add_delete(path="/user/{user_id}", handler=User.delete)
app.router.add_post(path="/authenticate", handler=authenticate)
app.router.add_post(path="/summary", handler=summarize)

app.on_startup.append(db_on_startup)

aiohttp.web.run_app(app)
