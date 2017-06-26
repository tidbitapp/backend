import aiopg
from typing import AsyncIterable, Union, Tuple

async def query(
    pool: aiopg.Pool,
    query: str,
    query_tuple: tuple = tuple()
) -> None:
  """
  Run a query without getting the result
  :param pool:
  :param query:
  :param query_tuple:
  :return:
  """
  connection = await pool.acquire()

  try:
    cursor = await connection.cursor()
    await cursor.execute(query, query_tuple)
  finally:
    pool.release(connection)

async def query_with_result(
    pool: aiopg.Pool,
    query: str,
    query_tuple: tuple = tuple()
) -> AsyncIterable[Union[Tuple, None]]:
  """
  Run a query and get the result piece-by-piece through an
  asynchronous generator
  :param pool:
  :param query:
  :param query_tuple:
  :return:
  """
  connection = await pool.acquire()

  try:
    cursor = await connection.cursor()
    await cursor.execute(query, query_tuple)

    record = await cursor.fetchone()
    while record is not None:
      yield record
      record = await cursor.fetchone()
  finally:
    pool.release(connection)