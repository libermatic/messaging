# messaging


## REST API

### `GET /services/<string:id>/balance`
Returns `balance` and `quota` along with other fields.

### `POST /services/<string:id>/<string:action>`
Attempts to execute a registered `action` for the **Service**.
Returns a **Message** when successful.

### `POST /login`
Accepetd params in body as JSON: `email` and `password`.
Returns `access_token` to be used in GraphQL requests.


## GraphQL API

### `POST /graf`
This endpoint is protected and needs the `access_token` received from `POST /login` as a _Bearer Token_ auth in the header.
All schema will be available on introspection.
