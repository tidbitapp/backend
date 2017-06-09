from aiohttp.web import Request, Response, json_response
from cerberus import Validator


async def create(request: Request) -> Response:
  """
  Create a user
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  validator = Validator({
    'firstName': {
      'required': True,
      'type': 'string'
    },
    'lastName': {
      'required': True,
      'type': 'string'
    },
    'username': {
      'required': True,
      'type': 'string'
    },
    'password': {
      'required': True,
      'type': 'string'
    }
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
  return Response()

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
  if not request.has_body and validator.validate(
    request_body
  ):
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Payload must be JSON with optional firstName, '
                   'lastName, username and password props',
        'errors': validator.errors
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
  return Response()
