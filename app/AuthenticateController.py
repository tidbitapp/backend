from aiohttp.web import Request, Response, json_response
from cerberus import Validator
import psycopg2
from .utils import session_token
from .db.UserRepository import UserRepository

async def authenticate(request: Request) -> Response:

  validator = Validator({
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
        'message': 'Payload must be JSON with username '
                   'and password props',
        'errors': validator.errors
      }
    )

  try:
    user = UserRepository(request.app['db_pool'])
    obtained_user = await user.getby_credentials(
      request_body.get('username'),
      request_body.get('password')
    )
  except (psycopg2.error, UserRepository.AuthError) as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not authenticate user',
        'errors': str(error)
      }
    )

  token = session_token.create({
    'user_id': obtained_user.user_id,
    'username': obtained_user.username,
    'last_login_at': obtained_user.last_login_at
  })

  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Successfully authenticated user',
      'data': token
    }
  )
