import aiopg
import pytz
from typing import NamedTuple, Union, List, Tuple
from datetime import datetime
import aitertools
from . import utils


class HistoryRepository:
	
  class HistoryCreate(NamedTuple):
    user_id: str
    document_id: str
    summarizer_type: str
    
  class HistoryView(NamedTuple):
    user_id: str
    document_id: str
    summarizer_type: str
    accessed_at: datetime

  def __init__(self, pool: aiopg.Pool):
    self.pool = pool

  async def startup(self) -> None:
    await utils.query(
      pool=self.pool,
      query=
      'CREATE TABLE history('
      ' id UUID DEFAULT uuid_generate_v4(),'
      ' user_id UUID            NOT NULL REFERENCES "user",'
      ' document_id UUID        NOT NULL REFERENCES document,'
      ' summarizer_type TEXT	NOT NULL,'
      ' accessed_at TIMESTAMPTZ NOT NULL,'
      ' PRIMARY KEY (id)'
      ');'
    )

  async def create(self, hist: HistoryCreate) -> None:
    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))

    await utils.query(
      pool=self.pool,
      query=
      'INSERT INTO "history"('
      ' user_id, document_id, summarizer_type, accessed_at'
      ') VALUES (%s, %s, %s, %s)',
      query_tuple=(
        hist.user_id, hist.document_id, hist.summarizer_type, current_time
      )
    )
