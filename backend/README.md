
# Backend - Trendit3

This document provides information on the API endpoints for the Trendit3 application.


## Setting up the Backend
### Install Dependencies

1. **Python 3.11.5** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - I recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:


```bash
  pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM I use to handle the lightweight SQL database. You'll primarily work in `app/__init__.py`and can reference `app/models`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension used to handle cross-origin requests from our frontend server.
    

## Authentication Endpoints
### User Registration

**Endpoint:** `/api/signup`  
**HTTP Method:** `POST`  
**Description:** Register a new user on the Trendit3 platform.  

Include the following JSON data in the request body:
```json
{
  "username": "username",
  "email": "user_email@example.com",
  "gender": "user_gender",
  "country": "user_country",
  "state": "user_state",
  "local_government": "user_local_government",
  "password": "user_password"
}
```

A verification code will be sent to user's Email. After which you'll get a response with a signup_token and 200 status code.
The signup token will be used to verify the user's Email in the next enpoint.
```json
{
  "status": "success",
  "message": "Verification code sent successfully",
  "status_code": 200,
  "signup_token": signup_token
}
```

If registration fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 400 Bad Request:** Invalid request payload.  
- **HTTP 409 Conflict:** User with the same email already exists.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

### User's Email Registration
**Endpoint:** `/api/verify-email`  
**Method:** `POST`  
**Description:** Verify user's email and register the user.  

Include the following JSON data in the request body:
```javascript
{
  "entered_code": "entered_code" // code entered by the user
  "signup_token": "signup_token", // string (received from the sign up endpoint)
}
```

A successful response will look like this:
```json
{
    "status": "success",
    "message": 'User registered successfully',
    "status_code": 201,
}
```
You can then go ahead to redirect user to login page.

If Email verification fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 400 Bad Request:** Invalid request payload.  
- **HTTP 409 Conflict:** User with the same email already exists.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  


### User Login
**Endpoint:** `/api/login`  
**HTTP Method:** `POST`  
**Description:** Authenticate a user and issue an access token.  

Include the following JSON data in the request body:
```json
{
  "email": "user_email@example.com",
  "password": "user_password"
}
```

If login is successful, you will receive a JSON response with a 200 OK status code. 
The response will include user's id.

```json
{
    "status": "success",
    "message": "User logged in successfully",
    "status_code": 200,
    "user_id": 123,
}
```

If Login fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** Invalid email or password.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

*Usage:*
- To register a new user, make a POST request to /api/signup with the required user data in the JSON format.
- To verify a new user, make a POST request to /api/verify-email with the required user data in the JSON format.
- To log in, make a POST request to /api/login with the user's email and password in the JSON format.
- Upon successful registration or login, the server will respond with 200 status code. Se below for details on how to access protected routes.

Please ensure that you handle errors and exceptions gracefully in your frontend application by checking the response status codes and displaying appropriate messages to the user.

#### Accessing Protected Routes
- To access a protected endpoints, you need to include the CSRF token in the X-CSRF-TOKEN header of your request. The CSRF token can be retrieved from a non-HTTP-only cookie (csrf_access_token) that is set when user logs in or refresh token.

- Here’s an example using JavaScript:
```js
import Cookies from 'js-cookie';

fetch('/api/protected', {
	method: 'GET',
  	headers: {
    	'X-CSRF-TOKEN': Cookies.get('csrf_access_token'),
  	},
  	credentials: 'include', // This is required to include the cookie in the request.
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => {
  	console.error('Error:', error);
});
```
A JWT token (access token) is already stored in an HTTP-only cookie, which is automatically sent with every request. So all you need to do is include the CSRF token in the X-CSRF-TOKEN header of your request.
If the JWT token and CSRF token are valid, you will be able to access the protected route. If either token is missing, expired, or invalid, you will receive an error response.

Please note that these tokens are sensitive information and should be handled securely. Do not expose these tokens in publicly accessible areas.

## Payment Endpoints
### Process Payment
**Endpoint:** `/api/payment`  
**HTTP Method:** POST  
**Description:** Process a payment for a user.  

Include the following JSON data in the request body:
```json
{
  "user_id": 123,
  "user_email": "user_email@example.com",
  "amount": 1000,
  "payment_type": "activation_fee"
}
```
If payment processing is successful, you will receive a JSON response with a 200 OK status code. The response will include a message and, in case of success, an authorization URL.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment initialized",
  "authorization_url": "user_authorization_url"
}
```

If payment processing fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 404 Not Found:** User not found.  
- **HTTP 409 Conflict:** Payment has already been made by the user.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  


### Verify Payment
**Endpoint:** /api/payment/verify  
**HTTP Method:** POST  
**Description:** Verify a payment for a user using the Paystack API.  

Include the following JSON data in the request body:
```json
{
    "transaction_id": "user_transactiod_id"
}
```
The transaction_id can be gotten from the arguments in the URL where user was redirected to after successful payment.

If payment verification is successful, you will receive a JSON response with a 200 OK status code. The response will include a message and payment details.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment successfully verified",
  "activation_fee_paid": true,
  "item_upload_paid": true
}
```

If payment verification fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 400 Bad Request:** Transaction verification failed.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

### Payment History
**Endpoint:** /api/payment/history   
**HTTP Method:** GET   
**Description:** Fetch the payment history for a user.   

Include the following JSON data in the request body:

```json
{
  "user_id": 123
}
```

If fetching the payment history is successful, you will receive a JSON response with a 200 OK status code. The response will include a message and the user's payment history.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment history fetched successfully",
  "payment_history": [
    {
      "id": 1,
      "user_id": 123,
      "amount": 1000,
      "payment_type": "activation_fee",
      "timestamp": "Sat, 05 Oct 2023 02:11:21 GMT"
    },
    {
      "id": 2,
      "user_id": 123,
      "amount": 500,
      "payment_type": "item_upload",
      "timestamp": "Sat, 05 Oct 2023 06:11:21 GMT"
    }
  ]
}
```

If fetching the payment history fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 404 Not Found:** User not found.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

### Webhook
**Endpoint:** /api/payment/webhook  
**HTTP Method:** POST  
**Description:** Handles a webhook for a payment.  

This endpoint is used for receiving and processing payment-related webhooks from Paystack. It verifies the signature of the webhook request, checks if the event is a successful payment event, and updates the user's membership status in the database.

- Usage: You should configure this endpoint as a webhook endpoint in your Paystack account settings.