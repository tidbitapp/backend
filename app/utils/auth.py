from . import session_token
from typing import Union
from aiohttp.web import Request


def get_request_session_token(request: Request) -> Union[str, None]:
  """
  Get session token from request
  :param request: aiohttp.web.Request
  :return: session token
  """
  authorization_header = request.headers.get('Authorization')
  if authorization_header is None:
    return None

  return authorization_header.replace('Bearer ', '')


def has_access_right(string_token: Union[str, None], user_id: str) -> bool:
  """
  Provided the current session, does a user have permission to
  private information of the user he/she is trying to access?
  :param string_token: session representation
  :param user_id: id of user being accessed
  :return: TRUE if he/she has permission, FALSE otherwise
  """
  if string_token is None:
    return False
  session = session_token.get_contents(string_token)
  if session is None:
    return False
  if user_id != session.get('user_id'):
    return False

  return True
