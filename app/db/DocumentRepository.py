import aiopg
from . import utils


class DocumentRepository:

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
