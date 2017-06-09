import aiopg
import pytz
from typing import NamedTuple, Union, List
from datetime import datetime


class UserRepository:

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
    class History(NamedTuple):
      url: str
      accessed_at: datetime
    first_name: str
    last_name: str
    username: str
    password: str
    joined_at: datetime
    last_login_at: datetime
    history: List[History]

  def __init__(self, pool: aiopg.Pool):
    self.pool = pool

  async def create(self, user: UserCreate) -> None:
    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))
    async with self.pool.cursor() as cursor:
      await cursor.execute(
        'INSERT INTO user ('
        ' firstName, lastName, username, password, joinedAt, lastLoginAt'
        ') VALUES (%s, %s, %s, %s, %s, %s)', (
          user.first_name, user.last_name, user.username,
          user.password, current_time, current_time
        )
      )

  async def updateby_id(self, user_id: int, user: UserUpdate) -> UserPublicView:
    async with self.pool.cursor() as cursor:
      await cursor.execute(
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
      updated_user_raw = await cursor.fetchone()
      return self.UserPublicView(*updated_user_raw)

  async def getby_id_public(self, user_id: int) -> Union[UserPublicView, None]:
    async with self.pool.cursor() as cursor:
      await cursor.execute(
        'SELECT firstName, lastName, username, password, joinedAt, lastLoginAt '
        'FROM user '
        'WHERE id=%s', (
          user_id,
        )
      )
      user_raw = await cursor.fetchone()

      if user_raw is None:
        return None

      return self.UserPublicView(*user_raw)

  async def getby_id_private(self, user_id: int) -> Union[UserPrivateView, None]:
    public_info_user = await self.getby_id_public(user_id)

    if public_info_user is None:
      return None

    async with self.pool.cursor() as cursor:
      await cursor.execute(
        'SELECT document.url, history.accessedAt '
        'FROM history, document '
        'WHERE history.userId=%s AND history.documentId == document.id', (
          user_id
        )
      )
      history_list_raw = await cursor.fetchall()

      return self.UserPrivateView(list(public_info_user).append(
        [self.UserPrivateView.History(*history_raw)
         for history_raw in history_list_raw]
      ))

  async def deleteby_id(self, user_id: int) -> None:
    async with self.pool.cursor() as cursor:
      await cursor.execute(
        'DELETE FROM user WHERE id=%s', (
          user_id
        )
      )
