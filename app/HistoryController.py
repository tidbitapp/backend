from aiohttp.web import Request, Response, json_response
import psycopg2
from typing import Union
from cerberus import Validator
from .utils import session_token
from .db.UserRepository import UserRepository
from .db.DocumentRepository import DocumentRepository
from .db.HistoryRepository import HistoryRepository
import app.UserController as UserController

async def index(request: Request) -> Response:
  """
  Return a list containing the history of the user's summarization requests
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  string_token = UserController.get_request_session_token(request)
  user_id = request.match_info['user_id']

  # Check that the user is logged
  if UserController.has_access_right(string_token, user_id) is False:
    return json_response(
        status=404,
        data={
          'status': 404,
          'message': 'The user must be logged in to access his or her history.'
        }
      )
      
   
  user = UserRepository(request.app['db_pool'])
  try:
    user_hist = await user.get_history_by_id(user_id)
  except psycopg2.Error as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not grab user\'s history information',
        'errors': error
      }
    )
    
  if user_hist is None:
    user_hist = []
  else:
    user_hist = list(map(lambda history_tuple: {
      'url': history_tuple[0],
      'summarizer_type': history_tuple[1],
      'accessedAt': str(history_tuple[2])
    }, user_hist.history))
      
  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'The history of the user has been successfully found.',
      'history': user_hist
    }
  )
