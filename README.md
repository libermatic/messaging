# messaging

## API

### `GET /accounts`

List of all **Accounts**

### `POST /accounts`

#### args

- `site` String. Required.
- `name` String.

A new **Account**

### `GET /accounts/<string:id>`

An **Account**

### `PUT /accounts/<string:id>`

#### args

- `name` String.

An updated **Account**

### `DELETE /accounts/<string:id>`

### `GET /accounts/<string:id>/key`

A key for the **Account**

### `GET /providers`

List of all **Providers**

### `POST /providers`

#### args

- `name` String. Required.
- `type` String.
- `base_url` String.

A new **Provider**

### `GET /providers/<string:id>`

A **Provider**

### `PUT /providers/<string:id>`

#### args

- `type` String.
- `base_url` String.

An updated **Provider**

### `DELETE /providers/<string:id>`

### `POST /providers/<string:id>/methods`

#### args

- `action` String. Required.
- `method` String. Choices: `GET`, `POST`
- `path` String.
- `args` [String].

Create a method for **Provider**

### `GET /providers/<string:id>/methods/<string:action>`

A method of the **Provider**

### `DELETE /providers/<string:id>/methods/<string:action>`

### `POST /providers/<string:id>/config`

#### args

- `auth_label` String. Required.
- `auth_location` String. Required. Choices: `header`, `body`, `query`
- `error_condition` Dictionary.
- `error_field` String.
- `error_value` String.
- `cost_field` String.
- `balance_field` String.

Sets **Provider** config

### `GET /accounts/<string:site>/services`

List of **Services** for the **Account**

### `POST /accounts/<string:site>/services`

#### args

- `name` String.
- `provider` String. A valid provider `id`.
- `quota` Integer.
- `vendor_key`: String.
- `unlimit`: Boolean.

Create a **Service** for the **Account**

### `GET /services`

List of all **Services**

### `GET /services/<string:id>`

A **Service**

### `PUT /services/<string:id>`

#### args

- `name` String.
- `provider` String. A valid provider `id`.
- `quota` Integer.
- `vendor_key`: String.
- `unlimit`: Boolean.

An updated **Service**

### `DELETE /services/<string:id>`

### `POST /services/<string:id>/static`

#### args

- `field`. String. Required.
- `value`. String.
- `location`. String. Required. Choices: `header`, `body`, `query`

Create a static key value pair for the **Service**

### `GET /services/<string:id>/static/<string:field>`

A static field for the **Service**

### `DELETE /services/<string:id>/static/<string:field>`

### `GET /services/<string:id>/balance`

Returns `balance` and `quota` along with other fields.

### `POST /services/<string:id>/balance`

#### args

- `amount`. Integer. Required.
- `reset`. Boolean. Required.

Loads `amount` to `balance` for the **Service**. Or resets `balance` to `quota`
for the **Service**. At least one if required.

### `POST /services/<string:id>/<string:action>`

Attempts to execute a registered `action` for the **Service**.
Returns a **Message** when successful.

### `GET /services/<string:service>/messages`

List of **Messages** for the **Service**

### `GET /messages`

List of all **Messages**
