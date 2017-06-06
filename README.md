# 📋 TidBit (Backend)
> Backend API Router for TidBit

TidBit is a document summarization application, currently with a Chrome extension front-end. When you hit the TidBit button on the Chrome extension, it will try to summarize and get the gist out of the webpage.

## Technologies
* 🐍 **Python** - Python 3 came out with asynchronous IO features, which will allow us to take greater advantage of concurrency and serve more requests for a given server.
* 🐋 **Docker** - Containerization and easy development/production environment bootstrapping
* 🐇 **RabbitMQ** - Message Queue that allows us to send messages between our backend and microservices, all with complex routing
* 📡 **Postgres** - Relational database of choice
* 📈 **Neo4J** - Graph-based database
* 📁 **HDFS** - Distributed Filesystem

## API Routes
The API routes are accessible under the `hostname/api/<current-version>` URL namespace. Output is in JSON format.

An access token can be obtained by loggin in and can be used on a request by specifying the Authorization header with the value: `Bearer <token>`.

Responses have the structure `{status, message, errors}`, where the `errors` prop is provided whenever the `status` denotes an HTTP error status.

* `/user`
  * `POST /` - Create a new user
    * Request: `{firstName, lastName, username, password}`
  * `GET /{userId}` - Get information about the user
    * With appropriate token:
      * Response: `{firstName, lastName, username, joinedAt, lastLoginAt, history: [{url, accessedAt}]}`
    * Without token:
      * Response: `{firstName, lastName, username, joinedAt, lastLoginAt}`
  * `POST /{userId}` - Update information about the user
    * Requires appropriate token
    * Request: `{firstName, lastName, username, password}`
  * `DELETE /{userId}` - Delete the user
    * Requires appropriate token
* `/authenticate`
  * `POST /` - Login with provided credentials and obtain a token
    * Request: `{username, password}`
    * Response: `{token}`
* `/summary`
  * `POST /` - Get a summary for the provided webpage contents
    * Request: `{url, domContent}`
    * Response: `{summary}`

## Relational Schema
The following entities exist in the database and represented in a normalized and relational fashion into a relational database.

* user
  * id - int
  * firstName - text
  * lastName - text
  * username - text
  * password - bytea
  * joinedAt - timestamp
  * lastLoginAt - timestamp
* history
  * id - int
  * userId - foreign(user, id)
  * documentId - foreign(document, id)
  * accessedAt - timestamp
* document
  * id - int
  * url - text
  * crawledAt - timestamp
