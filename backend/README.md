
# Backend - Trendit³

Trendit³ is a dynamic and innovative platform that provides users with an opportunity to earn money while engaging in a variety of daily activities.

This document provides information on the API endpoints for the Trendit³ application.


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
    
### Sending Form Data

Some endpoints will be recieving form data instead of the tranditional JSON data sent with every request.

Here is an example of how to send Form data to the update & create item endpoints:

``` javascript
const formData = new FormData();
formData.append('item_type', 'item_type');
formData.append('name', 'item_name');
// append other fields...
formData.append('item_img', selectedFile); // where selectedFile is a File object representing the uploaded image
fetch('/api/items/new', {
  method: 'POST',
  body: formData,
  headers: {
      'X-CSRF-TOKEN': Cookies.get('csrf_access_token')
  },
  credentials: 'include', // This is required to include the cookie in the request.
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => {
  console.error('Error:', error);
});

 ```

## Authentication Endpoints
_**Usage:**_

- To register a new user, make a POST request to `/api/signup` with the required user data in the JSON format.
- To verify a new user, make a POST request to `/api/verify-email` with the required user data in the JSON format.
- To log in, make a POST request to `/api/login` with the user's email and password in the JSON format.
- To verify 2 Factor Authentication Code, make a POST request to `/api/verify-2fa` with the entered code and 2FA token.
- Upon successful registration or login, the server will respond with 200 status code. See below for details on how to access protected routes.
    

Please ensure that errors and exceptions are handled gracefully in the frontend application by checking the response status codes and displaying appropriate messages to the user.

#### Accessing Protected Endpoints

- To access a protected endpoints, you need to include the CSRF token in the X-CSRF-TOKEN header of your request. The CSRF token can be retrieved from a non-HTTP-only cookie (csrf_access_token) that is set when user logs in or refresh token.
- Here’s an example using JavaScript:
    

``` javascript
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

A JWT token (access token) is already stored in an HTTP-only cookie, which is automatically sent with every request. So all you need to do is include the CSRF token in the X-CSRF-TOKEN header of your request. If the JWT token and CSRF token are valid, you will be able to access the protected route. If either token is missing, expired, or invalid, you will receive an error response.

Please note that these tokens are sensitive information and should be handled securely. Do not expose these tokens in publicly accessible areas.




### User Registration

**Endpoint:** `/api/signup`  
**HTTP Method:** `POST`  
**Description:** Register a new user on the Trendit³ platform.  
**Query Parameters:** `referrer_code` (optional)  

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

A verification code will be sent to user's Email. After which you'll get a response with a `signup_token` and 200 status code.
The `signup_token` will be used to verify the user's Email in the `/api/verify-email` endpoint.
```json
{
  "status": "success",
  "message": "Verification code sent successfully",
  "status_code": 200,
  "signup_token": "oikjasdkjsd;asmfdklksjdsaudjsamdsdsodsssd..."
}
```

If registration fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 400 Bad Request:** Invalid request payload.  
- **HTTP 409 Conflict:** User with the same email already exists.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

**_NOTE:_**  
The Trendit³ platform includes a referrer system, allowing users to refer others to the platform. Each referrer has a unique code associated with their account, which is appended to the signup URL. The client side is responsible for extracting this code and including it as a query parameter when making the signup API request.

When a user visits the signup URL, such as `www.trendit.com/signup/w7f8y3pl`, the referrer code (w7f8y3pl in this case) should be extracted from the URL path.

#### Example JavaScript code to extract referrer code:

``` javascript
// Extract referrer code from the URL
const referrerCode = window.location.pathname.split('/').pop();
 ```

The extracted referrer code should be included as a query parameter (referrer_code) when making the signup API request. For instance, `/api/signup?referrer_code=w7f8y3pl`.




### Resend Email Verification Code
**Endpoint:** `/api/resend-code`  
**Method:** `POST`  
**Description:** Resend Email verification code.

If verification code wasn't sent to user' email when signing up, this endpoint can be used to resend the code. All that is needed is the `signup_token` gotten from the `/api/signup` endpoint above.

Include the following JSON data in the request body:
```json
{
  "signup_token": "oikjasdkjsd;asmfdklksjdsaudjsamdsdsodsssd..."
}
```

A new code will be sent to user's email and a new `signup_token` will be returned in the response. The new `signup_token` is what should be used `/api/verify-email` endpoint.
```json
{
  "status": "success",
  "message": "New Verification code sent successfully",
  "status_code": 200,
  "signup_token": "Zs9asd0DHJHFGaJKdsuiuaJKfJadjamdsdsmujo783sd..."
}
```



### User's Email Verification
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
    "message": "User registered successfully",
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
**Description:** Authenticate a user and send a 2 Factor Authentication code to user's email.  

Include the following JSON data in the request body:
```json
{
  "email_username": "user_email@example.com",
  "password": "user_password"
}
```

If the email and password is correct, a 2 Factor Authentication Code will be sent to user's email. And `two_FA_token` will be included in the received JSON response with a 200 OK status code. 

The `two_FA_token` will be used to verify the 2 Factor Authentication Code in the `/api/verify-2fa` endpoint.

```json
{
    "status": "success",
    "message": "2 Factor Authentication code sent successfully",
    "status_code": 200,
    "two_FA_token": "ayhsjS3FsASSDyhjahdJsbvsJS909adaHJHJK..."
}
```

If Login fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** Invalid email or password.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  




### Verify 2 Factor Authentication Code
**Endpoint:** `/api/verify-2fa`  
**HTTP Method:** `POST`  
**Description:** Verify 2 Factor Authentication code and log user in.  

Include the following JSON data in the request body:
```json
{
  "entered_code": 189298,
  "two_FA_token": "ayhsjS3FsASSDyhjahdJsbvsJS909adaHJHJK..."
}
```

if the entered code is correct, user will be logged in successfully and a the following response will be returned.

```json
{
    "status": "success",
    "message": "User logged in successfully",
    "status_code": 200,
}
```
A successful login means an `access_token` and `csrf_access_token` has been included in the cookies.
The `access_token` is automatically sent with every request, but the `csrf_access_token` will needed to be manualy fetched from the cookies and placed in the X-CSRF-TOKEN header of request to protected endpoints.

_For more info, see Documentation above on accessing protected endpoints._




### User Logout
**Endpoint:** `/api/logout`  
**HTTP Method:** `POST`  
**Description:** Log out a user and delete access tokens from cookies.  
**Login Required:** True

The logout endpoint simply removes the x-srf-token and access token from the cookies, making it necessary to login again in other to get fresh access token stored in the http-only cookies.


If logout is successful, you will receive a JSON response with a 200 OK status code.

```json
{
    "message": "User logged out successfully",
    "status": "success",
    "status_code": 200,
}
```
 

## Payment Endpoints
The Payment endpoints are use to Initialize payments & process payments, verify payments and get payment history.
(payments are handled using the Paystack Payment Gateway.) 

It includes endpoints to pay `"Activation fee"` and `"Membership fee"`. It also to includes endpoints to credit user's wallet.

_**NOTE:**_ Currently, payments are made only in Naira, and support for other currencies will be added later on.

### Account Activation Fee
**Endpoint:** `/api/payment/account-activation-fee`  
**HTTP Method:** POST  
**Description:** Initialize a payment for account activation.  
**Login Required:** True

Include the following JSON data in the request body:
```json
{
  "amount": 1000,
}
```

On successful, request, this will return an authorization URL where users need to be redirected too in other to complete their payment.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment initialized",
  "authorization_url": "user_authorization_url",
  "payment_type": "account-activation-fee"
}
```

If payment Initialization fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 404 Not Found:** User not found.  
- **HTTP 409 Conflict:** Payment has already been made by the user.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  


### Membership Fee
**Endpoint:** `/api/payment/membership-fee`  
**HTTP Method:** POST  
**Description:** Initialize a payment for Monthly Membership fee.  
**Login Required:** True

Include the following JSON data in the request body:
```json
{
  "amount": 300,
}
```

On successful, request, this will return an authorization URL where users need to be redirected too in other to complete their payment.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment initialized",
  "authorization_url": "user_authorization_url",
  "payment_type": "membership-fee"
}
```

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

## Items Endpoints
Items is the name used to represent both productS and services uploaded to the Marketplace. So find below the endpoints to interact with items on the Marketplace.

### List All Items

**Endpoint:** `/api/items`  
**HTTP Method:** GET  
**Description:** Fetch all items in the database.  

**Query Parameters:**
- page: The page number to retrieve. Defaults to 1 if not provided.

A successful response will look like this:
```javascript
{
    "status": "success",
    "message": "Items fetched successfully",
    "status_code": 200,
    "total_items": 12, // total number of items available
    "items": [item1, item2, ...] // items on the current page
}
```
To fetch items from a specific page, include the `page` parameter in your request. For example, to fetch items from page 2, you would send a GET request to `/items?page=2.`


### Sending Form Data
The endpoints to create and update an items will be recieving form data instead of the tranditional JSON data sent with every request.

Here is an example of how to send Form data to the update & create item endpoints:

```javascript
const formData = new FormData();
formData.append('item_type', 'item_type');
formData.append('name', 'item_name');
// append other fields...
formData.append('item_img', selectedFile); // where selectedFile is a File object representing the uploaded image

fetch('/api/items/new', {
  method: 'POST',
  body: formData,
  headers: {
      'X-CSRF-TOKEN': Cookies.get('csrf_access_token')
  },
  credentials: 'include', // This is required to include the cookie in the request.
})
.then(response => response.json())
.then(data => console.log(data))
.catch((error) => {
  console.error('Error:', error);
});

```


### Create a New Item

**Endpoint:** `/api/items/new`  
**HTTP Method:** POST  
**Description:** Create a new item. This endpoint requires JWT authentication.

following the example above, you can send form data with the necessary fields to this endpoint `/api/items/new`:
```
item_type: "product", // either product or service
name: "Gorgeous Fresh Chips",
description: "This is a description"
price: 4000
category: "Groceries"
brand_name: "Oraimo"
size: "small"
color: "black"
material: "plastic"
phone: 09077648550
item_img: (binary data)
...

```

Upon successful creation, a 200 OK status code will be returned along with details of the uploaded item. A successful response will look like this:
```javascript
{
    "status": "success",
    "message": "Item created successfully",
    "status_code": 200,
    "item": {
        "brand_name": "Oraimo",
        "category": "Groceries",
        "colors": "black",
        "name": "Gorgeous Fresh Chips",
        "description": "This is a description",
        "id": 1,
        "item_img": "url/to/image",
        "material": "plastic",
        "phone": "09077648550",
        "price": 4000,
        "seller_id": 1, // this is the ID of the user that uploaded
        "sizes": "small",
        "slug": "gorgeous-fresh-chips",
        "total_comments": 0,
        "total_likes": 0,
        "views_count": 0,
        "created_at": "Tue, 17 Oct 2023 01:09:01 GMT",
        "updated_at": "Tue, 17 Oct 2023 01:09:01 GMT",
    },
}
```

### Update an Item

**Endpoint:** `/api/items/update/<int:item_id>`  
**HTTP Method:** PUT  
**Description:** Update an existing item. 

Include the necessary form data in the request body:
```
item_type: "new_item_type" // either product or service
name: "new item name"
...
item_img: (binary data)

```

A successful response will include a 200 OK status code and the details of the updated item:
```javascript
{
    "status": "success",
    "message": "Item updated successfully",
    "status_code": 200,
    "item": {updated item details...}
}

```

### Get a Single Item

**Endpoint:** `/api/items/<int:item_id>`  
**HTTP Method:** GET  
**Description:** Fetch a single item by its ID. 

A successful response will look like this:
```json
{
    "status": "success",
    "message": "Item fetched successfully",
    "status_code": 200,
    "item": {item details...}
}
```

### Delete an Item

**Endpoint:** `/api/items/delete/<int:item_id>`  
**HTTP Method:** DELETE  
**Description:** Delete an item by its ID. 

A successful response will look like this:
```json
{
    "status": "success",
    "message": "Item deleted successfully",
    "status_code": 200
}
```

Please remember to handle errors and exceptions gracefully in your frontend application by checking the response status codes and displaying appropriate messages to the user.