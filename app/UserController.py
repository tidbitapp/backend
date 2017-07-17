from aiohttp.web import Request, Response, json_response
import psycopg2

from cerberus import Validator
from .utils import auth
from .db.UserRepository import UserRepository


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

  try:
    request_body = await request.json()
  except:
    request_body = None

  if not validator.validate(request_body):
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
    await user.create(UserRepository.UserCreate(
      request_body.get('firstName'), request_body.get('lastName'),
      request_body.get('username'), request_body.get('password')
    ))
  except psycopg2.Error as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not create user',
        'errors': str(error)
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
  string_token = auth.get_request_session_token(request)
  user_id = request.match_info['user_id']
  user = UserRepository(request.app['db_pool'])

  if auth.has_access_right(string_token, user_id) is False:
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
          'joinedAt': obtained_user.joined_at.isoformat(),
          'lastLoginAt': obtained_user.last_login_at.isoformat()
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
        'errors': str(error)
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
        'joinedAt': obtained_user.joined_at.isoformat(),
        'lastLoginAt': obtained_user.last_login_at.isoformat(),
        'history': list(map(lambda history_tuple: {
          'url': history_tuple[0],
          'accessedAt': str(history_tuple[1])
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

  try:
    request_body = await request.json()
  except:
    request_body = None

  if not validator.validate(request_body):
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Payload must be JSON with optional firstName, '
                   'lastName, username and password props',
        'errors': validator.errors
      }
    )

  user_token = auth.get_request_session_token(request)
  user_id = request.match_info['user_id']
  user = UserRepository(request.app['db_pool'])

  if auth.has_access_right(user_token, user_id) is False:
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
        'errors': str(error)
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
  user_token = auth.get_request_session_token(request)
  user_id = request.match_info['user_id']
  user = UserRepository(request.app['db_pool'])

  if auth.has_access_right(user_token, user_id) is False:
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
        'errors': str(error)
      }
    )

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Successfully deleted user'
    }
  )
