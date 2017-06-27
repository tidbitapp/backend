import aiopg
from . import utils


class HistoryRepository:

  def __init__(self, pool: aiopg.Pool):
    self.pool = pool

  async def startup(self) -> None:
    await utils.query(
      pool=self.pool,
      query=
      'CREATE TABLE history('
      ' id UUID DEFAULT uuid_generate_v4(),'
      ' user_id UUID            NOT NULL REFERENCES "user",'
      ' document_id UUID        NOT NULL UNIQUE REFERENCES document,'
      ' accessed_at TIMESTAMPTZ NOT NULL,'
      ' PRIMARY KEY (id)'
      ');'
    )
