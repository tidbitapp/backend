from asynctest import TestCase, MagicMock, CoroutineMock
from aiopg import Pool, Cursor, Connection
from tidbit.app.db.HistoryRepository import HistoryRepository
from datetime import datetime

class HistoryRepositoryTest(TestCase):

  mock_cursor = MagicMock(Cursor)
  mock_connection = MagicMock(Connection)
  mock_connection.cursor = CoroutineMock(
    return_value=mock_cursor
  )
  postgres_pool_mock = MagicMock(Pool)
  postgres_pool_mock.acquire = CoroutineMock(
    return_value=mock_connection
  )

  async def tearDown(self):
    self.mock_cursor.reset_mock()
    self.postgres_pool_mock.reset_mock()
    
  async def test_create(self):
    accessed_at = datetime.now()
    hist = HistoryRepository(self.postgres_pool_mock)
    await hist.create(HistoryRepository.HistoryCreate(
      "user_id", "document_id", "summarizer_type"
    ))

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
