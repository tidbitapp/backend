import aiopg
import pytz
from typing import NamedTuple, Union, List, Tuple
from datetime import datetime
import aitertools
from . import utils


class DocumentRepository:
	
  class DocumentCreate(NamedTuple):
    user_id: str
    url: str
    contents: str
    
  class DocumentView(NamedTuple):
    document_id: str
    user_id: str
    url: str
    contents: str
    summarized_at: datetime

  def __init__(self, pool: aiopg.Pool):
    self.pool = pool

  async def startup(self) -> None:
    await utils.query(
      pool=self.pool,
      query=
      'CREATE TABLE document('
      ' id UUID DEFAULT uuid_generate_v4(),'
      ' user_id UUID              NOT NULL REFERENCES "user",'
      ' url TEXT                  NOT NULL,'
      ' contents TEXT             NOT NULL,'
      ' summarized_at TIMESTAMPTZ NOT NULL,'
      ' PRIMARY KEY (id)'
      ');'
    )
    
  async def create(self, doc: DocumentCreate) -> Union[
    DocumentView, None
  ]:
    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))

    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'INSERT INTO "document"('
      ' user_id, url, contents, summarized_at'
      ') VALUES (%s, %s, %s, %s) '
      'RETURNING id, user_id, url, contents, summarized_at',
      query_tuple=(
        doc.user_id, doc.url, doc.contents, current_time
      )
    )

    doc_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if doc_raw is None:
      return None
    return self.DocumentView(*doc_raw)
    
  async def getby_id(self, doc_id: str) -> Union[
    DocumentView, None
  ]:
    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'SELECT id, user_id, url, contents, summarized_at '
      'FROM "document" '
      'WHERE id=%s',
      query_tuple=(doc_id,)
    )

    doc_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if doc_raw is None:
      return None
    return self.DocumentView(*doc_raw)
    
  async def getby_url(self, url: str) -> Union[
    DocumentView, None
  ]:
    datasource_generator = utils.query_with_result(
      pool=self.pool,
      query=
      'SELECT id, user_id, url, contents, summarized_at '
      'FROM "document" '
      'WHERE url=%s',
      query_tuple=(url,)
    )

    doc_raw = await aitertools.anext(
      datasource_generator,
      None
    )
    await datasource_generator.aclose()

    if doc_raw is None:
      return None
    return self.DocumentView(*doc_raw)
