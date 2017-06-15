from aiohttp.web import Request, Response, json_response
import psycopg2
from typing import Union
from cerberus import Validator
from .utils import session_token
from .db.user import UserRepository


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


def has_access_right(string_token: Union[str, None], user_id: int) -> bool:
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
  if user_id != int(session.get('user_id')):
    return False

  return True


async def create(request: Request) -> Response:
  """
  Create a user
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  validator = Validator({
    'firstName': {'required': True, 'type': 'string'},
    'lastName': {'required': True, 'type': 'string'},
    'username': {'required': True, 'type': 'string'},
    'password': {'required': True, 'type': 'string'}
  })

  request_body = await request.json()
  if not (request.has_body and validator.validate(
      request_body
  )):
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Payload must be JSON with firstName, lastName, '
                   'username and password props',
        'errors': validator.errors
      }
    )

  try:
    user = UserRepository(request.app['db_pool'])
    user.create(UserRepository.UserCreate(
      request_body.get('firstName'), request_body.get('lastName'),
      request_body.get('username'), request_body.get('password')
    ))
  except psycopg2.Error as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not create user',
        'errors': error
      }
    )

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Successfully created user'
    }
  )

async def get(request: Request) -> Response:
  """
  Return information about a user
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  string_token = get_request_session_token(request)
  user_id = int(request.match_info['user_id'])
  user = UserRepository(request.app['db_pool'])

  if has_access_right(string_token, user_id) is False:
    try:
      obtained_user = await user.getby_id_public(user_id)
    except psycopg2.Error as error:
      return json_response(
        status=400,
        data={
          'status': 400,
          'message': 'Could not grab user information',
          'errors': error
        }
      )

    if obtained_user is None:
      return json_response(
        status=404,
        data={
          'status': 404,
          'message': 'User does not exist'
        }
      )

    return json_response(
      status=200,
      data={
        'status': 200,
        'message': 'User found',
        'data': {
          'firstName': obtained_user.first_name,
          'lastName': obtained_user.last_name,
          'username': obtained_user.username,
          'joinedAt': obtained_user.joined_at,
          'lastLoginAt': obtained_user.last_login_at
        }
      }
    )

  try:
    obtained_user = await user.getby_id_private(user_id)
  except psycopg2.Error as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not grab user information',
        'errors': error
      }
    )

  if obtained_user is None:
    return json_response(
      status=404,
      data={
        'status': 404,
        'message': 'User does not exist'
      }
    )

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'User found',
      'data': {
        'firstName': obtained_user.first_name,
        'lastName': obtained_user.last_name,
        'username': obtained_user.username,
        'joinedAt': obtained_user.joined_at,
        'lastLoginAt': obtained_user.last_login_at,
        'history': list(map(lambda history_tuple: {
          'url': history_tuple[0],
          'accessedAt': history_tuple[1]
        }, obtained_user.history))
      }
    }
  )

async def update(request: Request) -> Response:
  """
  Update information about a user
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  validator = Validator({
    'firstName': {'type': 'string'},
    'lastName': {'type': 'string'},
    'username': {'type': 'string'},
    'password': {'type': 'string'}
  })

  request_body = await request.json()
  if not (request.has_body and validator.validate(
    request_body
  )):
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Payload must be JSON with optional firstName, '
                   'lastName, username and password props',
        'errors': validator.errors
      }
    )

  user_token = get_request_session_token(request)
  user_id = int(request.match_info['user_id'])
  user = UserRepository(request.app['db_pool'])

  if has_access_right(user_token, user_id) is False:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Invalid permissions to update the user'
      }
    )

  try:
    await user.updateby_id(user_id, UserRepository.UserUpdate(
      request_body.get('firstName'), request_body.get('lastName'),
      request_body.get('username'), request_body.get('password')
    ))
  except psycopg2.Error as error:
    json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not update user',
        'errors': error
      }
    )

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Successfully updated user'
    }
  )

async def delete(request: Request) -> Response:
  """
  Delete a user
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  user_token = get_request_session_token(request)
  user_id = int(request.match_info['user_id'])
  user = UserRepository(request.app['db_pool'])

  if has_access_right(user_token, user_id) is False:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Invalid permissions to delete the user'
      }
    )

  try:
    await user.deleteby_id(user_id)
  except psycopg2.Error as error:
    json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not delete user',
        'errors': error
      }
    )

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Successfully deleted user'
    }
  )
