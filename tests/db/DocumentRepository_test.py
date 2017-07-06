from asynctest import TestCase, MagicMock, CoroutineMock
from aiopg import Pool, Cursor, Connection
from tidbit.app.db.DocumentRepository import DocumentRepository
from datetime import datetime

class DocumentRepositoryTest(TestCase):

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
    summarized_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(return_value=(
      "document_id", "user_id", "www.test.com", "contents",
      summarized_at
    ))
    
    doc = DocumentRepository(self.postgres_pool_mock)
    await doc.create(DocumentRepository.DocumentCreate(
      "user_id", "wwww.test.com", "contents"
    ))

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()
    
  async def test_getby_id(self):
    summarized_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(return_value=(
      "document_id", "user_id", "www.test.com", "contents",
      summarized_at
    ))
    
    doc = DocumentRepository(self.postgres_pool_mock)
    obtained_doc = await doc.getby_id(1)

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()
    
    self.assertIsInstance(obtained_doc, DocumentRepository.DocumentView)
    self.assertEqual(obtained_doc.document_id, "document_id")
    self.assertEqual(obtained_doc.user_id, "user_id")
    self.assertEqual(obtained_doc.url, "www.test.com")
    self.assertEqual(obtained_doc.contents, "contents")
    self.assertIs(obtained_doc.summarized_at, summarized_at)
    
    
  async def test_getby_url(self):
    summarized_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(return_value=(
      "document_id", "user_id", "www.test.com", "contents",
      summarized_at
    ))
    
    doc = DocumentRepository(self.postgres_pool_mock)
    obtained_doc = await doc.getby_url("www.test.com")

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()
    
    self.assertIsInstance(obtained_doc, DocumentRepository.DocumentView)
    self.assertEqual(obtained_doc.document_id, "document_id")
    self.assertEqual(obtained_doc.user_id, "user_id")
    self.assertEqual(obtained_doc.url, "www.test.com")
    self.assertEqual(obtained_doc.contents, "contents")
    self.assertIs(obtained_doc.summarized_at, summarized_at)
	  
  
