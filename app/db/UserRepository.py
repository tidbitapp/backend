import aiopg
import pytz
from typing import NamedTuple, Union, List, Tuple
from datetime import datetime
import aitertools
from . import utils


class UserRepository:
  """
  Abstracts over our interactions with user data.

  An instance of Postgres pool object is dependency-injected upon
  instantiation and on each database action, we acquire a free connection
  from the pool. After we have acquire our wanted results, we then
  release the connection.

  For added typing benefits, all methods accept a type-hinted class
  subclassing NamedTuple.
  """

  class UserCreate(NamedTuple):
    first_name: str
    last_name: str
    username: str
    password: str

  class UserUpdate(NamedTuple):
    first_name: Union[str, None]
    last_name: Union[str, None]
    username: Union[str, None]
    password: Union[str, None]

  class UserPublicView(NamedTuple):
    first_name: str
    last_name: str
    username: str
    password: str
    joined_at: datetime
    last_login_at: datetime

  class UserPrivateView(NamedTuple):
    first_name: str
    last_name: str
    username: str
    password: str
    joined_at: datetime
    last_login_at: datetime
    history: List[Tuple[str, datetime]]

  class UserCredentialView(NamedTuple):
    user_id: str
    username: str
    last_login_at: datetime

  class AuthError(BaseException):
    pass

  def __init__(self, pool: aiopg.Pool):
    self.pool = pool

  async def startup(self) -> None:
    await utils.query(
      pool=self.pool,
      query=
      'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
      'CREATE TABLE "user"('
      ' id UUID DEFAULT uuid_generate_v4(),'
      ' first_name TEXT           NOT NULL,'
      ' last_name TEXT            NOT NULL,'
      ' username VARCHAR(30)      NOT NULL UNIQUE,'
      ' password VARCHAR(100)     NOT NULL,'
      ' joined_at TIMESTAMPTZ     NOT NULL,'
      ' last_login_at TIMESTAMPTZ NOT NULL,'
      ' PRIMARY KEY (id)'
      ');'
    )

  async def create(self, user: UserCreate) -> None:
    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))

    await utils.query(
      pool=self.pool,
      query=
      'INSERT INTO "user"('
      ' first_name, last_name, username, password, joined_at, '
      ' last_login_at) VALUES (%s, %s, %s, %s, %s, %s)',
      query_tuple=(
        user.first_name, user.last_name, user.username,
        user.password, current_time, current_time
      )
    )

  async def updateby_id(self, user_id: str, user: UserUpdate) -> Union[
    UserPublicView, None
  ]:
    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'UPDATE "user" '
      'SET first_name=COALESCE(%s, first_name),'
      ' last_name=COALESCE(%s, last_name), '
      ' username=COALESCE(%s, username), '
      ' password=COALESCE(%s, password) '
      'WHERE id=%s '
      'RETURNING'
      ' first_name, last_name, username,'
      ' password, joined_at, last_login_at',
      query_tuple=(
        user.first_name, user.last_name, user.username,
        user.password, user_id
      )
    )

    updated_user_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if updated_user_raw is None:
      return None
    return self.UserPublicView(*updated_user_raw)

  async def getby_id_public(self, user_id: str) -> Union[
    UserPublicView, None
  ]:
    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'SELECT first_name, last_name, username, password,'
      ' joined_at, last_login_at '
      'FROM "user" '
      'WHERE id=%s',
      query_tuple=(user_id,)
    )

    user_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if user_raw is None:
      return None
    return self.UserPublicView(*user_raw)

  async def getby_id_private(self, user_id: str) -> Union[
    UserPrivateView, None
  ]:
    public_info_user = await self.getby_id_public(user_id)

    if public_info_user is None:
      return None

    history_list_raw = utils.query_with_result(
      pool=self.pool,
      query=
      'SELECT document.url, history.accessed_at '
      'FROM history, document '
      'WHERE history.user_id=%s'
      ' AND history.document_id = document.id',
      query_tuple=(user_id,)
    )

    params = list(public_info_user)
    params.append(
      await aitertools.alist(history_list_raw)
    )
    await history_list_raw.aclose()

    return self.UserPrivateView(*params)

  async def getby_credentials(
      self,
      username: str,
      password: str
  ) -> UserCredentialView:
    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'SELECT id, username, last_login_at '
      'FROM "user"'
      'WHERE username=%s AND password=%s',
      query_tuple=(username, password)
    )

    user_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if user_raw is None:
      raise self.AuthError("Could not authenticate user")

    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))
    await utils.query(
      pool=self.pool,
      query=
      'UPDATE "user" '
      'SET last_login_at=%s '
      'WHERE id=%s',
      query_tuple=(current_time, user_raw[0])
    )

    return self.UserCredentialView(
      str(user_raw[0]), user_raw[1], user_raw[2]
    )

  async def deleteby_id(self, user_id: str) -> None:
    await utils.query(
      pool=self.pool,
      query=
      'DELETE FROM "user" WHERE id=%s',
      query_tuple=(user_id,)
    )
