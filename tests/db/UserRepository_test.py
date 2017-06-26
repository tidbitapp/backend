from asynctest import TestCase, MagicMock, CoroutineMock
from aiopg import Pool, Cursor, Connection
from app.db.UserRepository import UserRepository
from datetime import datetime


class UserRepositoryTest(TestCase):

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
    user = UserRepository(self.postgres_pool_mock)
    await user.create(UserRepository.UserCreate(
      "Joe", "Schmoe", "someUsername", "somePass"
    ))

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()

  async def test_delete(self):
    user = UserRepository(self.postgres_pool_mock)
    await user.deleteby_id(1)

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()

  async def test_update_exists(self):
    joined_at = datetime.now()
    last_login_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(return_value=(
      "firstName", "lastName", "username", "password",
      joined_at, last_login_at
    ))

    user = UserRepository(self.postgres_pool_mock)
    updated_user = await user.updateby_id(1, UserRepository.UserUpdate(
      None, None, None, None
    ))

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()

    self.assertIsInstance(updated_user, UserRepository.UserPublicView)
    self.assertEqual(updated_user.first_name, "firstName")
    self.assertEqual(updated_user.last_name, "lastName")
    self.assertEqual(updated_user.username, "username")
    self.assertEqual(updated_user.password, "password")
    self.assertIs(updated_user.joined_at, joined_at)
    self.assertIs(updated_user.last_login_at, last_login_at)

  async def test_update_notexists(self):
    self.mock_cursor.fetchone = CoroutineMock(return_value=None)

    user = UserRepository(self.postgres_pool_mock)
    updated_user = await user.updateby_id(1, UserRepository.UserUpdate(
      None, None, None, None
    ))

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()

    self.assertEqual(updated_user, None)

  async def test_getpublic_exists(self):
    joined_at = datetime.now()
    last_login_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(return_value=(
      "firstName", "lastName", "username", "password",
      joined_at, last_login_at
    ))

    user = UserRepository(self.postgres_pool_mock)
    obtained_user = await user.getby_id_public(1)

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()

    self.assertIsInstance(obtained_user, UserRepository.UserPublicView)
    self.assertEqual(obtained_user.first_name, "firstName")
    self.assertEqual(obtained_user.last_name, "lastName")
    self.assertEqual(obtained_user.username, "username")
    self.assertEqual(obtained_user.password, "password")
    self.assertIs(obtained_user.joined_at, joined_at)
    self.assertIs(obtained_user.last_login_at, last_login_at)

  async def test_getpublic_notexists(self):
    self.mock_cursor.fetchone = CoroutineMock(return_value=None)

    user = UserRepository(self.postgres_pool_mock)
    obtained_user = await user.getby_id_public('1')

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()

    self.assertEqual(obtained_user, None)

  async def test_getprivate(self):
    returned_user = UserRepository.UserPublicView(
      "firstName", "lastName", "username", "password",
      datetime.now(), datetime.now()

    )

    history_object = ("someUrl", datetime.now())
    mock = CoroutineMock()
    mock.side_effect = [history_object, None]
    self.mock_cursor.fetchone = mock

    user = UserRepository(self.postgres_pool_mock)
    user.getby_id_public = CoroutineMock(
      return_value=returned_user
    )
    obtained_user = await user.getby_id_private('1')

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.assertEqual(
      self.mock_cursor.fetchone.call_count,
      2
    )
    user.getby_id_public.assert_called_once()

    self.assertIsInstance(obtained_user, UserRepository.UserPrivateView)
    self.assertListEqual(obtained_user.history, [history_object])

  async def test_getbycredentials_exists(self):
    sample_id = 'id-sample1'
    sample_username = 'username-sample1'
    sample_last_login_at = datetime.now()
    self.mock_cursor.fetchone = CoroutineMock(
      return_value=(
        sample_id, sample_username, sample_last_login_at
      )
    )

    user = UserRepository(self.postgres_pool_mock)
    obtained_user = await user.getby_credentials(
      "someUsername",
      "somePassword"
    )

    self.assertEqual(obtained_user.user_id, sample_id)
    self.assertEqual(obtained_user.username, sample_username)
    self.assertEqual(
      obtained_user.last_login_at,
      sample_last_login_at
    )

  async def test_getbycredentials_notexists(self):
    self.mock_cursor.fetchone = CoroutineMock(
      return_value=None
    )

    user = UserRepository(self.postgres_pool_mock)
    with self.assertRaises(UserRepository.AuthError):
      await user.getby_credentials(
        "someUsername",
        "somePassword"
      )

    self.postgres_pool_mock.acquire.assert_called_once()
    self.postgres_pool_mock.release.assert_called_once()
    self.mock_cursor.execute.assert_called_once()
    self.mock_cursor.fetchone.assert_called_once()
