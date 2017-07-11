from aiohttp.web import Request, Response, json_response
import psycopg2
from typing import Union
from cerberus import Validator
from .utils import session_token
from .db.UserRepository import UserRepository
from .db.DocumentRepository import DocumentRepository
from .db.HistoryRepository import HistoryRepository
import app.UserController as UserController
from .summarizers import Summarizer
from bs4 import BeautifulSoup
import urllib.request
from readability import readability


def extract_text_from_html(html: Union[str, None]) -> str:
  """
  Given a string with HTML, it extracts the text within it
  Credit: part of this code was based on Hugh Bothwell's code as found
  in: https://stackoverflow.com/questions/22799990/beatifulsoup4-get-text-still-has-javascript
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  soup = BeautifulSoup(html, "html.parser")
  
  # Remove all script and style tags in the html
  for s in soup(["style", "script"]):
    s.extract()

  text = soup.get_text()
  # Break the text into lines and also remove all leading and trailing space 
  # in any of the lines
  lines = (line.strip() for line in text.splitlines())
  # Break multi-headlines into individual lines
  chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
  # Remove all blank lines
  text = ' '.join(chunk for chunk in chunks if chunk)
  
  return text
  
def extract_article(url: Union[str, None]) -> str:
  page = urllib.request.urlopen(url)
  html = page.read()

  article = readability.Document(html).summary()
  
  return extract_text_from_html(article)
  
async def get_summarizer_types(request: Request) -> Response:
  """
  Return the available summarizer types (i.e. the types of algorithms
  available to use for summarization)
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'The following are the available summarizer types.',
      'data': {
      'summarizerTypes': str(Summarizer.SUMMARIZER_TYPES)
     }
    }
  )
  

async def summarize(request: Request) -> Response:
  """
  Return a summarized version of the given document
  :param request: aiohttp.web.Request
  :return: Coroutine object that returns aiohttp.web.Response
  """
  
  validator = Validator({
    'url': {'required': True, 'type': 'string'},
    'domContent': {'required': True, 'type': 'string'},
    'summarizerType': {'required': True, 'type': 'string'}
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
        'message': 'Payload must be JSON with user ID, URL of document, '
                   'DOM content of the document\'s website and the type of'
                   'summarizer',
        'errors': validator.errors
      }
    )
  
  # Ensure that the user is logged
  string_token = UserController.get_request_session_token(request)
  user_id = request.match_info['user_id']

  """if UserController.has_access_right(string_token, user_id) is False:
    return json_response(
        status=404,
        data={
          'status': 404,
          'message': 'The user must be logged in to access his or her history.'
        }
      )"""
  
  # Extract the text of the document from the DOM content
  try:
    text = extract_article(request_body.get('url'))
  except urllib.error.HTTPError as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not access the web page through the given URL.',
        'errors': str(error)
      }
    )
   
  # Summarize the document 
  summarizer_type = request_body.get('summarizerType')
  if summarizer_type not in Summarizer.SUMMARIZER_TYPES:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Can not summarize document.',
        'errors': 'The given summarizer type is not valid.'
      }
    )
  
  # Summarize the text
  summary = Summarizer.summarize(text, summarizer_type)
  
  # Check whether this Document has been summarized before.
  # If not, create the Document object in the DB that represents the document
  # that was summarized.
  doc = DocumentRepository(request.app['db_pool'])
  new_doc = await doc.getby_url(request_body.get('url'))
  if new_doc is None:
    try:
      new_doc = await doc.create(DocumentRepository.DocumentCreate(
        user_id, request_body.get('url'),
        request_body.get('domContent')
      ))
    except psycopg2.Error as error:
      return json_response(
        status=400,
        data={
          'status': 400,
          'message': 'Could not create Document instance',
          'errors': str(error)
        }
      )
    
  # Create the History object in the DB that records that this user summarized
  # this document at this specific time.
  try:
    hist = HistoryRepository(request.app['db_pool'])
    await hist.create(HistoryRepository.HistoryCreate(
      user_id, new_doc.document_id, 
      summarizer_type
    ))
  except psycopg2.Error as error:
    return json_response(
      status=400,
      data={
        'status': 400,
        'message': 'Could not create History instance',
        'errors': str(error)
      }
    )
   
  return json_response(
    status=200,
    data={
      'status': 200,
      'message': 'Summarization was successful',
      'data': {
		'summarizerType': summarizer_type,
        'summary': summary
      }
    }
  )
