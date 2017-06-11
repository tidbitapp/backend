import aiopg
import pytz
from typing import NamedTuple, Union, List, Tuple
from datetime import datetime


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

  def __init__(self, pool: aiopg.Pool):
    self. pool = pool

  async def create(self, user: UserCreate) -> None:
    connection = await self.pool.acquire()

    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))
    await connection.execute(
      'INSERT INTO user ('
      ' firstName, lastName, username, password, joinedAt, '
      ' lastLoginAt ) VALUES (%s, %s, %s, %s, %s, %s)', (
        user.first_name, user.last_name, user.username,
        user.password, current_time, current_time
      )
    )

    self.pool.release(connection)

  async def updateby_id(self, user_id: int, user: UserUpdate) -> Union[
    UserPublicView, None
  ]:
    connection = await self.pool.acquire()
    await connection.execute(
      'UPDATE user '
      'SET firstName=COALESCE(firstName, %s),'
      ' lastName=COALESCE(lastName, %s), '
      ' username=COALESCE(username, %s), '
      ' password=COALESCE(password, %s) '
      'WHERE id=%s '
      'RETURNING'
      ' firstName, lastName, username,'
      ' password, joinedAt, lastLoginAt', (
        user.first_name, user.last_name, user.username,
        user.password, user_id
      )
    )
    updated_user_raw = await connection.fetchone()

    self.pool.release(connection)

    if updated_user_raw is None:
      return None
    return self.UserPublicView(*updated_user_raw)

  async def getby_id_public(self, user_id: int) -> Union[
    UserPublicView, None
  ]:
    connection = await self.pool.acquire()
    await connection.execute(
      'SELECT firstName, lastName, username, password,'
      ' joinedAt, lastLoginAt '
      'FROM user '
      'WHERE id=%s',
      (user_id,)
    )
    user_raw = await connection.fetchone()

    self.pool.release(connection)

    if user_raw is None:
      return None
    return self.UserPublicView(*user_raw)

  async def getby_id_private(self, user_id: int) -> Union[
    UserPrivateView, None
  ]:
    public_info_user = await self.getby_id_public(user_id)

    if public_info_user is None:
      return None

    connection = await self.pool.acquire()
    await connection.execute(
      'SELECT document.url, history.accessedAt '
      'FROM history, document '
      'WHERE history.userId=%s AND history.documentId == document.id',
      (user_id,)
    )
    history_list_raw = await connection.fetchall()
    self.pool.release(connection)

    params = list(public_info_user)
    params.append(history_list_raw)
    return self.UserPrivateView(*params)

  async def deleteby_id(self, user_id: int) -> None:
    connection = await self.pool.acquire()

    await connection.execute(
      'DELETE FROM user WHERE id=%s', (
        user_id
      )
    )

    self.pool.release(connection)
