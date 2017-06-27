import jwt
from os import getenv
from datetime import datetime, timedelta
import pytz
from typing import Union


def create(payload: dict) -> str:
  def datetime_future(hours: int):
    now = datetime.now(tz=pytz.timezone('US/Eastern'))
    hours_added = timedelta(hours=hours)
    return now + hours_added

  jwt_secret = getenv('JWT_SECRET')
  payload['exp'] = datetime_future(24)

  return jwt.encode(payload, jwt_secret, algorithm='HS256').decode(
    'utf-8'
  )


def get_contents(token: str) -> Union[dict, None]:
  jwt_secret = getenv('JWT_SECRET')

  try:
    contents = jwt.decode(token, jwt_secret)
  except jwt.exceptions.InvalidTokenError:
    return None

  return contents
