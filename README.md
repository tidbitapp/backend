# 📋 TidBit (Backend)
> Backend API for TidBit

TidBit is a document summarization application, currently with a Chrome extension front-end. When you hit the TidBit button on the Chrome extension, it will try to summarize and get the gist out of the webpage.

## Technologies
* 🐍 **Python** - Python 3 came out with asynchronous IO features, which will allow us to take greater advantage of concurrency and serve more requests for a given server.
* 🐋 **Docker** - Containerization and easy development/production environment bootstrapping
* 🐇 **RabbitMQ** - Message Queue that allows us to send messages between our backend and microservices, all with complex routing
* 📡 **Postgres** - Relational database of choice
* 📈 **Neo4J** - Graph-based database
* 📁 **HDFS** - Distributed Filesystem

## Getting Started
Make sure to have Docker and Docker-Compose installed. Then, follow through the following steps:
1. `cd` to the base of the project directory
2. Rename `backend_sample.env` and `relational_db_sample.env` to `backend.env` and `relational_db.env`
3. Fill in the appropriate information in both `backend.env` and `relational_db.env`, making sure to specify all values accordingly
4. Run `docker-compose build`
5. Run `docker-compose up` and now, you should be able to access the API routes at the localhost or whatever hostname your copy of Docker is working on!
6. To shut containers down, run `docker-compose down`

When you update the source code, you will have to run `docker-compose down` followed by `docker-compose up` again. These commands must always be executed at the base of the project directory!

## API Routes
The API routes are accessible under the `hostname/api/<current-version>` URL namespace. Output is in JSON format.

An access token can be obtained by loggin in and can be used on a request by specifying the Authorization header with the value: `Bearer <token>`.

Responses have the structure `{status, message, errors}`, where the `errors` prop is provided whenever the `status` denotes an HTTP error status.

* `/user`
  * `POST /` - Create a new user
    * Request: `{firstName, lastName, username, password}`
  * `GET /{userId}` - Get information about the user
    * With appropriate token:
      * Response: `{firstName, lastName, username, joinedAt, lastLoginAt, history: [{url, accessedAt, summarizer_type}]}`
    * Without token:
      * Response: `{firstName, lastName, username, joinedAt, lastLoginAt}`
  * `POST /{userId}` - Update information about the user
    * Requires appropriate token
    * Request: `{firstName, lastName, username, password}`
  * `DELETE /{userId}` - Delete the user
    * Requires appropriate token
  * `POST /{user_id}/summary` - Get a summary for the provided webpage contents
    * Request: `{url, domContent, summarizerType}`
    * Response: `{summary, summarizerType}`
    * Requires appropriate token
  * `GET /{user_id}/history` - Get a history of the documents this user has summarized
    * Request: `None`
    * Response: `{history: [{url, accessedAt, summarizer_type}]}`
    * Requires appropriate token
* `/authenticate`
  * `POST /` - Login with provided credentials and obtain a token
    * Request: `{username, password}`
    * Response: `{token}`
* `/summary`
  * `POST /` - Get a summary of the page content
    * Request: `{url, domContent:optional, summarizerType}`
  * `GET /types` - Returns a list of the available summarization algorithms.
    * Request: None
    * Response: `{summarizerTypes}`

## Relational Schema
The following entities exist in the database and represented in a normalized and relational fashion into a relational database.

* user
  * id - uuid
  * first_name - text
  * last_name - text
  * username - varchar(30)
  * password - varchar(100)
  * joined_at - timestamptz
  * last_login_at - timestamptz
* history
  * id - uuid
  * user_id - foreign(user, id)
  * document_id - foreign(document, id)
  * summarizer_type - text
  * accessed_at - timestamptz
* document
  * id - int
  * user_id - foreign(user, id)
  * url - text
  * contents - text
  * summarized_at - timestamptz
