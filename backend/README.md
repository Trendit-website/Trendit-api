
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
    
### Response Structure:

**Every API endpoint ensures a consistent response structure comprising:**

- `status` (string): Signifying the request outcome, either "success" or "failed".
- `message` (string): A message that conveys supplementary information regarding the request status
- `status_code` (integer): Represents the HTTP status code, reflecting the success or failure of the request.
    

These elements are foundational across all endpoints. For endpoint-specific details, refer to the individual documentation sections.


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
**Error Handling**  
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

**Error Handling**  
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

**Error Handling**  
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


### Forgot Password
**Endpoint:** `/api/forgot-password`  
**HTTP Method:** `POST`  
**Description:** used if to reset password if it's forgotten.  

This endpoint requires either the the user's email, or username in the body of the reequest. A six digit reset code will be sent to user's email. This reset code will need to be sent to `/api/reset-password` endpoint to verify and change password.
```json
{
    "email_username": "trendit_user@gmail.com"
}
```

If reset code is sent successful, you will receive a JSON response with a 200 OK status code and a `reset_token`.

```json
{
    "email": "trendit_user@gmail.com",
    "message": "Password reset code sent successfully",
    "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...",
    "status": "success",
    "status_code": 200
}
```
**Error Handling**  
If an eeror occurs in the process, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  




### Verify Password Reset Code
**Endpoint:** `/api/reset-password`  
**HTTP Method:** `POST`  
**Description:** verify reset code and change password.

The reset code, new password and reset token is required in the request's body.
```json
{
    "entered_code": 641092,
    "new_password": "new.password",
    "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ..."
}
```

This endpoint will check if the entered code is correct and update the user's password with the provided `new password`.

if `entered_code` is correct, you will receive a JSON response with a 200 OK status code and appropriate message.
```json
{
    "message": "Password changed successfully",
    "status": "success",
    "status_code": 200
}
```
**Error Handling**  
If an eeror occurs in the process, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** reset code is invalid or expired.  
- **HTTP 404 Not Found:** reset token not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request. 




### Resend Password Rest Code
**Endpoint:** `/api/resend-code?code_type=pwd-reset`  
**HTTP Method:** `POST`  
**Description:** Resend code to save reset password.  
**Query Parameters:** `code_type=pwd-reset`

The resend code endpoint is used to resend the six-digit code that should have been sent to the user in the first place.

In this case, this endpoint with the Query Parameter `code_type=pwd-reset` will resend the password reset code that was sent by the `/api/forgot-password` endpoint.

This endpoint only requires either username or email.
```json
{
    "email_username": "trendit_user@gmail.com"
}
```

If request is successful, the reset code will be sent and a new reset token will be returned in the response.
```json
{
    "message": "Password reset code sent successfully",
    "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJm...",
    "status": "success",
    "status_code": 200
}
```

**Error Handling**  
If an error occurs in the process, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  







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

_**NOTE:**_ Currently, payments are made only in Naira, and support for other currencies will be added later on. Documentation will updated when the support is added.




### Account Activation Fee
**Endpoint:** `/api/payment/account-activation-fee`  
**HTTP Method:** POST  
**Description:** Initialize a payment for account activation.  
**Login Required:** True

This endpoint will set up the payment process for `account-activation-fee`. A Paystack authorization URL will be returned in the response for user to complet their payment. Once payment is complete use will automatically be redirected back to the homepage with a Transaction reference in as the query parameter.
For instance, after a successful payment the user could be redirected to this URL.

`https://trendit3.vercel.app/homepage?trxref=bsvxk9cpxx`

As you can see there is `trxref` query parameter in the URL. This query parameter will be needed in the endpoint to verify payments. 

So to initialize payment, the amount is needed in the request's body:
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
**Error Handling**  
If payment Initialization fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 409 Conflict:** Payment has already been made by the user.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  


### Membership Fee
**Endpoint:** `/api/payment/membership-fee`  
**HTTP Method:** POST  
**Description:** Initialize a payment for Monthly Membership fee.  
**Login Required:** True

This endpoint will set up the payment process for `membership-fee`. A Paystack authorization URL will be returned in the response for user to complet their payment. Once payment is complete use will automatically be redirected back to the homepage with a Transaction reference in as the query parameter.
For instance, after a successful payment the user could be redirected to this URL.

`https://trendit3.vercel.app/homepage?trxref=bsvxk9cpxx`

As you can see there is `trxref` query parameter in the URL. This query parameter will be needed in the endpoint to verify payments. 

So to initialize payment, the amount is needed in the request's body:
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



### Credit Wallet
**Endpoint:** `/api/payment/credit-wallet`  
**HTTP Method:** POST  
**Description:** Initialize a payment for a user to credit their Trendit wallet.  
**Login Required:** True

This endpoint will set up the payment process to credit user's wallet. A Paystack authorization URL will be returned in the response for user to complete their payment. Once payment is complete use will automatically be redirected back to the homepage with a Transaction reference in as the query parameter.
For instance, after a successful payment the user could be redirected to this URL.

`https://trendit3.vercel.app/homepage?trxref=bsvxk9cpxx`

As you can see there is `trxref` query parameter in the URL. This query parameter will be needed in the endpoint to verify payments. 

So to initialize payment, the amount is needed in the request's body:
```json
{
  "amount": 300,
}
```
If payment processing is successful, you will receive a JSON response with a 200 OK status code. The response will include an authorization URL. This is where you redirect user's to make their payments to credit their Trendit wallet. A successful response should look like this.
``` json
{  
    "status": "success",
    "status_code": 200,
    "message": "Payment initialized",  
    "payment_type": "credit-wallet",
    "authorization_url": "https://user_authorization_url"
}

 ```
**Error Handling**  
If payment processing fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### Verify Payment
**Endpoint:** /api/payment/verify  
**HTTP Method:** POST  
**Description:** Verify a payment for a user using the Paystack API.  


This endpoint is necessary immediately after being redirected from Paystack.  
As explained the docs above, immediately after payment, users gets redirected back to Trendit³ site, with a `trxref` query parameter in the URL. The value of this query parameter needs to be sent to `/api/payment/verify` in other to confirm that the payment was made. And if the payment was made successfully, the user record will be updated accordingly in the Trendit³ database.

Include the following JSON data in the request body:
```json
{
    "reference": "8j9onvy39z" // the value of trxref
}
```
The reference can be gotten from the arguments in the URL where user was redirected to after successful payment.

If payment verification is successful, you will receive a JSON response with a 200 OK status code. The response will include a message and payment details.
```json
{
  "status": "success",
  "status_code": 200,
  "message": "Payment successfully verified",
  "activation_fee_paid": true,
}
```
**Error Handling**  
If payment verification fails, you will receive a JSON response with details about the error, including the status code.
- **HTTP 400 Bad Request:** Transaction verification failed.  
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.  

### Payment History
**Endpoint:** /api/payment/history   
**HTTP Method:** GET   
**Description:** Fetch the payment history for logged in user.  
**Login Required:** True

This endpoint fetches the payment history of the the current logged in User.  
If fetching the payment history is successful, you will receive a JSON response with a 200 OK status code. The response will include the user's payment history.

``` json
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
**Error Handling**  
If fetching the payment history fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 404 Not Found:** User not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

### Webhook
**Endpoint:** /api/payment/webhook  
**HTTP Method:** POST  
**Description:** Handles a webhook for a payment.  

This endpoint is meant for Paystack only and request from any other party won't work.  
It is used for receiving and processing payment-related webhooks from Paystack. It verifies the signature of the webhook request, checks if the event is a successful payment event, and updates the user's record in the database.

- Usage: You should configure this endpoint as a webhook endpoint in your Paystack account settings.








## Items Endpoints (products & services)
Items is the name used to represent both products and services uploaded to the Marketplace. The items endpoints consist of endpoints to fetch all items, fetch a single item, upload items, update items, and delete item.


### Fetch All Items
**Endpoint:** `/api/items`  
**HTTP Method:** GET  
**Description:** Fetch all Items (products and services) from the Marketplace.  
**Query Parameters:** `page` - The page number to retrieve. It Defaults to 1 if not provided.

This endpoint fetches all products & services available in the Marketplace.  
For better performance, the returned items are paginated. Only 10 items are returned per page. To retrieve more items from a particular page, include the `page` query parameter in the endpoint.

**Example Request:**  `GET /api/items?page=1`

**Key Response Details:**

- `total` (integer): The total number of items available in the Marketplace.
- `all_items` (list): A list containing details of products and services (up to 10 per page).
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve items.



**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Products & services fetched successfully",
    "status_code": 200,
    "current_page": 1,
    "total_pages": 7,
    "total": 30,
    "all_items": [
        {
            "brand_name": "Apple",
            "category": "tech",
            "colors": "black",
            // ... (item details)
        },
        {
            "brand_name": "Samsung",
            "category": "tech",
            "colors": "white",
            // ... (item details)
        },
        // ... (up to 10 items per page)
    ]
}
```
**To fetch items from a specific page:**  
Include the `page` query parameter in the endpoint. For example, to fetch items from page 2, send a GET request to `/api/items?page=2`.


**Error Handling**  
If fetching items fails, you will receive a JSON response with details about the error, including the status code.

- HTTP 500 Internal Server Error: An error occurred while processing the request.






### Fetch Single Item
**Endpoint:** `/api/items/{item_id_slug}`  
**HTTP Method:** GET  
**Description:** Retrieve details for a single a single item using it's ID or slug.  

**Path Parameter:**
- `{item_id_slug}` (required): The ID or slug of the item to retrieve.


This endpoint fetches details for a specific item (product or service) in the Marketplace. You can use either the item's ID or slug in the path parameter.  

**Example Request:**   
- Fetch an item using it's id: `/api/items/2`
- Fetch an item using it's slug: `/api/items/surface-duo-t63a`

Ensure you replace surface-duo-t63a with the actual item ID or slug you want to retrieve. Adjust the request accordingly based on your specific requirements.


**Key Response Details:**

- `item` (object): An object containing details of the requested item.


A successful response will look like this:

``` json
{
    "status": "success",
    "message": "product fetched successfully",
    "status_code": 200,
    "item": {
        "brand_name": "Apple",
        "category": "tech",
        "colors": "black",
        "created_at": "Thu, 07 Dec 2023 17:39:49 GMT",
        "description": "This is a description",
        "id": 1,
        "item_img": "http://res.cloudinary.com/dcozguaw3/img.png",
        "item_type": "product",
        "material": "plastic",
        "name": "surface duo",
        "phone": "09077648550",
        "price": 9900,
        "sizes": "large",
        "slug": "surface-duo-t63a",
        "total_comments": 0,
        "total_likes": 0,
        "updated_at": "Thu, 07 Dec 2023 17:39:49 GMT",
        "views_count": 0
        "seller": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        },
    }
}

 ```
**Error Handling**  
If fetching the item details fails (e.g., if the item with the provided ID or slug does not exist), you will receive a JSON response with details about the error, including the status code.

- HTTP 404 Not Found: product or service not found.
- HTTP 500 Internal Server Error: An error occurred while processing the request.






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


### Create (Upload) a New Item
**Endpoint:** `/api/items/new`  
**HTTP Method:** POST  
**Description:** Create a new item (product or service) in the Marketplace.  
**Login Required:** True

To create(upload) an item, you need to send a form data to this endpoint.    
Following the example above on how to send form data, you can send form data with the necessary fields to this endpoint `/api/items/new`:

**Form Data Parameters (for POST request):**
- `country` (required): The country of the user.
- `state` (required): The state of the user.
- `city` (required): The city (LGA) of the user.
- `item_type` (required): The type of the item. Options: `product` or `service`.
- `name` (required): The name of the item.
- `description` (required): A description of the item.
- `price` (required): The price of the product or service.
- `category` (required): The category to which the item belongs.
- `brand_name` (required): The brand name of the item.
- `size` (optional): The size of the item (if applicable).
- `color` (optional): The color of the item (if applicable).
- `material` (optional): The material of the item (if applicable).
- `phone` (required if it's a service): The contact phone number associated with the item.
- `item_img` (required): Binary data representing the image of the item.

**Key Response Details:**

- `item` (object): An object containing details of the created item.

Upon successful creation, a 200 OK status code will be returned along with details of the uploaded item.  
**A Successful Response Example:**
```json
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
        "sizes": "small",
        "slug": "gorgeous-fresh-chips",
        "total_comments": 0,
        "total_likes": 0,
        "views_count": 0,
        "created_at": "Tue, 17 Oct 2023 01:09:01 GMT",
        "updated_at": "Tue, 17 Oct 2023 01:09:01 GMT",
        "seller": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        },
    }
}
```

**Error Handling**  
If creating the item fails (e.g., due to validation errors or server issues), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.








### Update an Item
**Endpoint:** `/api/items/update/{item_id_slug}`  
**HTTP Method:** `PUT`  
**Description:** Update details for an existing Item (product or service) in the Marketplace.  
**Login Required:** True

**Path Parameter:**
- `{item_id_slug}` (required): The ID or slug of the item to update.

Include the needed form data in the request body:  
**Form Data Parameters:**
- `country` (required): The country of the user.
- `state` (required): The state of the user.
- `city` (required): The city (LGA) of the user.
- `item_type` (required): The type of the item. Options: `product` or `service`.
- `name` (required): The updated name of the item.
- `description` (required): The updated description of the item.
- `price` (required): The updated price of the product or service.
- `category` (required): The updated category to which the item belongs.
- `brand_name` (required): The updated brand name of the item.
- `size` (optional): The updated size of the item (if applicable).
- `color` (optional): The updated color of the item (if applicable).
- `material` (optional): The updated material of the item (if applicable).
- `phone` (required): The updated contact phone number associated with the item.
- `item_img` (optional): Binary data representing the updated image of the item.


**Key Response Details:**

- `item` (object): An object containing details of the updated item.

**A Successful Response Example:**
```json
{
    "message": "Item updated successfully",
    "status": "success",
    "status_code": 200,
    "item": {
        "brand_name": "Samsung",
        "category": "tech",
        "colors": "black",
        "created_at": "Thu, 07 Dec 2023 17:40:53 GMT",
        "description": "This is a new product",
        "id": 2,
        "item_img": null,
        "item_type": "product",
        "material": "iron",
        "name": "Galaxy Z Fold",
        "phone": "09077648550",
        "price": 100,
        "sizes": "large",
        "slug": "galaxy-z-fold",
        "total_comments": 0,
        "total_likes": 0,
        "views_count": 0,
        "updated_at": "Sat, 09 Dec 2023 07:17:21 GMT",
        "seller": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        }
    }
}
```

**Error Handling**  
If updating the item fails (e.g., due to validation errors or server issues), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 404 Not Found:** The requested item was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### Delete an Item
**Endpoint:** `/api/items/delete/{item_id_slug}`  
**HTTP Method:** `DELETE`  
**Description:** Delete an existing item (product or service) using its ID or slug.  
**Login Required:** True  

**Path Parameter:**
- `{item_id_slug}` (required): The ID or slug of the item to delete.


**Example Request:**  

- Delete an item using it's id: `/api/items/delete/2`
- Delete an item using it's slug: `/api/items/delete/surface-duo-t63a`


**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the item was deleted successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Item deleted successfully",
    "status_code": 200
}
```

**Error Handling**  
If deleting the item fails (e.g., if the item with the provided ID or slug does not exist), you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 404 Not Found:** The requested item was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

Please remember to handle errors and exceptions gracefully in your frontend application by checking the response status codes and displaying appropriate messages to the user.


---

## Item Interactions
The endpoint in this category are used to Interact with an Item (product or service).  
Item interactions includes likes, views and comments.



### Like Item
**Endpoint:** `/api/items/<item_id_slug>/like`  
**HTTP Method:** `POST`  
**Description:** Add a like to a specific product or service in the Marketplace.  
**Login Required:** True

**Path Parameter:**
- `{item_id_slug}` (required): The ID or slug of the item to like.

**Example Request:**  `POST /api/items/galaxy-z-fold/like`

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the like was added successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "product liked successfully",
    "status_code": 200
}
```

**Error Handling**  
If adding a like to the item fails (e.g., if the item with the provided ID or slug does not exist), you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 404 Not Found:** The requested item was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### View Item

**Endpoint:** `/api/items/<item_id_slug>/view`  
**HTTP Method:** `POST`  
**Description:** Register a view for a specific product or service in the Marketplace.  
**Login Required:** True

**Path Parameter:**
- `{item_id_slug}` (required): The ID or slug of the item to view.


**Example Request:**  `POST /api/items/galaxy-z-fold/view`


**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the view was registered successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "product viewed successfully",
    "status_code": 200
}
```

**Error Handling**  
If registering a view for the item fails (e.g., if the item with the provided ID or slug does not exist), you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 404 Not Found:** The requested item was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.





### Add Comment to Item

**Endpoint:** `/api/items/comment`  
**HTTP Method:** `POST`  
**Description:** Add a comment to a product or service in the Marketplace.  
**Login Required:** True

**Request Body:**
- `comment` (required): The text content of the comment.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the comment was added successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `comment_details` (object): An object containing details of the added comment.

**Request Body Example:**
```json
{
    "comment": "This is the first comment ever on Trendit³"
}
```

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Comment added successfully",
    "status_code": 200,
    "comment_details": {
        "comment": "This is the second comment ever on trendit3",
        "created_at": "Sat, 09 Dec 2023 11:39:50 GMT",
        "id": 3,
        "item_id": 2,
        "updated_at": "Sat, 09 Dec 2023 11:39:50 GMT",
        "user": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        }
    }
}
```

**Error Handling**  
If adding a comment to the item fails (e.g., if the required data is missing or the item does not exist), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 401 Unauthorized:** User is not logged in.
- **HTTP 404 Not Found:** The requested item was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

---
## Location Endpoints
The endpoints in this collection can be used to get supported countries, states and local government area.


**Note:**  
The `supported countries` endpoint includes a curated list of countries deemed relevant to the Trendit platform, containing 7 entries. This selection is based on the regions that Paystack currently supports. 

Please bare in mind that, at the moment, Trendit³ is set up to only process payments in Nigeria's currency. But that could change later on as the Trendit³ platform grows and reaches a wide area of audience.


### Fetch Supported Countries
**Endpoint:** `/api/countries`  
**HTTP Method:** GET  
**Description:** Fetch supported countries.

This endpoint returns the list of countries currently supported by Paystack for payment processing. 

**Note:**  
Trendit³ intends allows users to make payments in their local currencies. So to ensure a seamless payment experience, the platform utilizes the country data provided by Paystack.

**Key response details:**

- `total` (integer): Indicates the total number of countries returned.
- `countries` (list): Holds the total countries and their respective data.    
    - `name` (string): The name of the country.
    - `iso_code` (string): A unique code representing the country.
    - `currency_code` (string): A unique code representing the currency.
    

**A successful response will look like this:**

``` json
{
    "status": "success",
    "message": "Countries retrieved",
    "status_code": 200,
    "total": 7,
    "countries": [
        {
            "currency_code": "NGN",
            "iso_code": "NG",
            "name": "Nigeria"
        },
        {
            "currency_code": "GHS",
            "iso_code": "GH",
            "name": "Ghana"
        },
        {...},
    ]
}
```

**Error Handling**  
If the request fails, you will receive a JSON response with details about the error, including the status code.

- HTTP 500 Internal Server Error: An error occurred while processing the request.




### Fetch States
**Endpoint:** `/api/states?country=Nigeria`  
**HTTP Method:** GET  
**Description:** Fetch the states for a specified country.  
**Query Parameters:** `country` (required)   


This endpoint returns a list of states within the specified country. The list is particularly useful for users to select their specific region when providing location information.


**Key response details:**

- `total` (integer): The total number of states available for the specified country.
- `states` (list): A list of dictionaries containing state information.
    - `name` (string): The name of the state.
    - `state_code` (string): A unique code representing the state.

**Example Request:**

`GET /api/states?country=Nigeria`

**A successful response will look like this:**

``` json
{
    "status": "success",
    "message": "States in Nigeria retrieved",
    "status_code": 200,
    "total": 36,
    "states": [
        {"name": "Abia State", "state_code": "AB"},
        {"name": "Adamawa State", "state_code": "AD"},
        {"name": "Akwa Ibom State", "state_code": "AK"},
        {"name": "...", "state_code": "..."},
        {...}
    ]
}
 ```

**Error Handling**  
If the request fails, you will receive a JSON response with details about the error, including the status code.

- HTTP 500 Internal Server Error: An error occurred while processing the request.





### Fetch State's Local Governments
**Endpoint:** `/api/states/lga/<state_name>`  
**HTTP Method:** GET  
**Description:** Fetch the local governments of a specified state. 


This endpoint returns a list of local government areas in a given state. The list is particularly useful for users to select their specific region when providing location information.


**Key response details:**
- `total` (integer): The total number of local governments in the specified state.
- `state_lga` (list): A list containing the local governments.


**Example Request:**
`GET /api/states/lga/lagos`

**A successful response will look like this:**

``` json
{
    "status": "success",
    "message": "Local governments for Lagos fetched successfully",
    "status_code": 200,
    "total": 20,
    "state_lga": [
        "Agege",
        "Ajeromi-Ifelodun",
        "Alimosho",
        "Amuwo-Odofin",
        "Apapa",
        "Badagry",
        "Epe",
        "Eti-Osa",
        "Ibeju-Lekki",
        "Ifako-Ijaiye",
        "Ikeja",
        "Ikorodu",
        "Kosofe",
        "Lagos Island",
        "Lagos Mainland",
        "Mushin",
        "Ojo",
        "Oshodi-Isolo",
        "Shomolu",
        "Surulere"
    ],
}
 ```
**Error Handling**  
If the request fails, you will receive a JSON response with details about the error, including the status code.

- HTTP 500 Internal Server Error: An error occurred while processing the request.
---
## Tasks Endpoints

One of the core features of Trendit³ is allowing users to create task for other users to perform.  
There are two types of task which include, `Advert Task` and `Engagement Task`

The endpoints in this section includs:

- **For All Tasks:**
    - `Fetch all Tasks`: Fetches both advert and engagement tasks.
    - `Fetch Tasks by the current User`: Fetches all advert and engagement task created by the current logged in user.
    - `Fetch a Single Task`: Fetches a specific task and its details.
    - `Create Task with wallet`: Creates a new task, using user's wallet.
    - `Create Tasks with Payment Gateway`: Creates a new task, using Paystack.
- **For Advert Tasks:**
    - `Fetch Advert Tasks`: Fetchs all advert task.
    - `Fetch Advert Tasks for Platfrom`: Fetches all advert task created for a specific social platfrom.
    - `Fetch Advert Tasks Grouped by Field`: Fetches all advert task, but grouped by a specified field (e.g: paltform)
- **For Engagement Tasks:**
    - `Fetch Engagement Tasks`: Fetch all engagement tasks.
    - `Fetch Engagement Tasks Grouped by Field`: Fetches all engagement tasks, but grouped by a specified field, (e.g: goal)



### Fetch All Tasks
**Endpoint:** `/api/tasks`  
**HTTP Method:** `GET`  
**Description:** Fetch both advert and engagement tasks.  
**Query Parameters:** `page` (optional): The page number to retrieve. Defaults to 1 if not provided.

This endpoint fetches all advert and engagement tasks.  
For better performance, the tasks are paginated. So by default, 10 Tasks are returned per page. To get more Tasks from a particular page, the query parameter page needs to be present the endpoint.


**Key Response Details:**

- `total` (integer): The total number of Tasks on Trendit³.
- `all_tasks` (list): A list containing all tasks. (up to 10 per page).
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve tasks.

**A Successful Response Example:**
```json
{
    "message": "All Tasks fetched successfully",
    "status": "success",
    "status_code": 200,
    "total_pages": 1
    "current_page": 1,
    "total": 2,
    "all_tasks": [
        {
            "caption": "ujhbujnb",
            "gender": "Male",
            "hashtags": "#hjsdf, kskj, kslkf",
            "id": 2,
            "media_path": "https://cloudinary.com/img.png",
            "payment_status": "Complete",
            "platform": "youtube",
            "posts_count": 3,
            "target_country": "Nigeria",
            "target_state": "Lagos",
            "task_key": "vie26tzysa",
            "type": "advert"
            "creator": {
                "id": 1,
                "username": "trendit3_user",
                "email": "trendit3_user@gmail.com"
            }
        },
        {
            "account_link": "https://hjsj.com",
            "engagements_count": 1,
            "goal": "Follow my account",
            "id": 1,
            "media_path": null,
            "payment_status": "Complete",
            "platform": "instagram",
            "task_key": "bwg2ublad3",
            "type": "engagement"
            "creator": {
                "id": 1,
                "username": "trendit3_user",
                "email": "trendit3_user@gmail.com"
            }
        },
    ],
}
```

To fetch Tasks from a specific page, include the page query parameter in the endpoint. For example, to fetch Tasks from page 2, send a GET request to api/tasks?page=2.


**Error Handling**  
If fetching Tasks fails, you will receive a JSON response with details about the error, including the status code.

- HTTP 500 Internal Server Error: An error occurred while processing the request.




### Fetch All Tasks by Current User
**Endpoint:** `/api/current-user/tasks`  
**HTTP Method:** `GET`  
**Description:** Fetch both advert and engagement tasks created by the currently logged in user.  
**Query Parameters:** `page` (optional): The page number to retrieve. Defaults to 1 if not provided.  
**Login Required:** True

This endpoint is quite similar to the `Fetch All Tasks` endpoint above, except this time it returns all tasks created by currently logged in user.

**Key Response Details:**
- `total` (integer): The total number of Tasks on Trendit³.
- `all_tasks` (list): A list containing all tasks. (up to 10 per page).
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve tasks.

**A Successful Response Example:**
```json
{
    "message": "All Tasks fetched successfully",
    "status": "success",
    "status_code": 200,
    "total_pages": 1
    "current_page": 1,
    "total": 2,
    "all_tasks": [retrieved tasks...],
}
```

To fetch Tasks from a specific page, include the page query parameter in the endpoint. For example, to fetch Tasks from page 2, send a GET request to api/tasks?page=2.


**Error Handling**  
If fetching Tasks fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.











### Fetch Single Task

**Endpoint:** `/api/tasks/{task_id_key}`  
**HTTP Method:** `GET`  
**Description:** Retrieve detailed information about a specific task based on its unique ID or key.  
**Path Parameter::** `{task_id_key}` (required)

This endpoint allows you to fetch a single task by providing its unique identifier in the URL.

**Path Parameter::**
- `{task_id_key}` (required): The unique identifier of the task. Example: `/api/tasks/123` or `/api/tasks/vie26tzyx1`

**Key Response Details:**

- `task` (object): Detailed information about the specified task.
    - `creator` (object): details on the user that created the task

**A Successful Response Example:**
```json
{
    "message": "Task fetched successfully",
    "status": "success",
    "status_code": 200,
    "task": {
        "caption": "ujhbujnb",
        "gender": "Male",
        "hashtags": "#hjsdf, kskj, kslkf",
        "id": 123,
        "media_path": "https://cloudinary.com/img.png",
        "payment_status": "Complete",
        "platform": "youtube",
        "posts_count": 3,
        "target_country": "Nigeria",
        "target_state": "Lagos",
        "task_key": "vie26tzyx1",
        "type": "advertisement"
        "creator": {
            "id": 1,
            "username": "trendit3_user",
            "email": "trendit3_user@gmail.com"
        }
    }
}
```
**Error Handling**  
If fetching Task fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.





### Create New Task

**Endpoint:** `/api/tasks/new?payment_method=trendit_wallet`  
**HTTP Method:** `POST`  
**Description:** Create a new task.   
**Query Parameters:**  `payment_method` (required):

In this endpoint, payment is required before the task is created. If the payment method is "trendit_wallet," the user's wallet will be used for payment. If the payment method is "payment_gateway," a Paystack authorization URL will be returned for redirection to complete the payment.

**Query Parameters:**
- `payment_method` (required): The payment method for task creation. Options: `trendit_wallet` or `payment_gateway`.

**Form Data Parameters (for POST request):**
- `task_type` (required): The type of task. Options: `advert` or `engagement`.
- `caption` (required for advert tasks): The caption or title for the advertisement task.
- `platform` (required): The platform for the task. Example: `youtube`, `instagram`.
- `amount` (required): The amount to be paid in Naira.
- `target_country` : The target country for the task.
- `target_state` : The target state within the country for the task.
- `gender` (optional): The gender associated with the task.
- `hashtags` (required for advert tasks): Any hashtags associated with the advertisement task.
- `media` (optional): URL of media associated with the task.
- `posts_count` (required for advert tasks): The number of times the task can be performed by others.
- `goal` (required for engagement tasks): The goal for engagement tasks, e.g., "Follow my account."
- `account_link` (required for engagement tasks): The link to the social media account to engage with.
- `engagements_count` (required for engagement tasks): The number of times the task can be performed by others.


**Key Response Details:**

- If payment method is `trendit_wallet`:
  - `message` (string): A success message indicating that the task has been created.
  - `task` (object): Details of the newly created task

- If payment method is `payment_gateway`:
  - `authorization_url` (string): The Paystack authorization URL. Redirect the user to this URL to complete the payment.

**A Successful Response Example (trendit_wallet):**
```json
{
    "message": "Task created successfully. Payment made using Trendit³ Wallet.",
    "status": "success",
    "status_code": 201,
    "task": {
        "caption": "ujhbujnb",
        "gender": "Male",
        "hashtags": "#hjsdf, kskj, kslkf",
        "id": 4,
        "media_path": null,
        "payment_status": "Complete",
        "platform": "youtube",
        "posts_count": 3,
        "target_country": "Nigeria",
        "target_state": "Lagos",
        "task_key": "leplrxf9sd",
        "type": "advert"
        "creator": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        },
    }
}
```

**A Successful Response Example (payment_gateway):**
```json
{
    "authorization_url": "https://checkout.paystack.com/jph2o4hhupfkj72",
    "message": "Payment initialized",
    "payment_type": "task_creation",
    "status": "success",
    "status_code": 200
}
```
After a user successfully makes payment using paystack, the user could be redirected back to Trendit³ site.  
`https://trendit3.vercel.app/homepage?trxref=bsvxk9cpxx`

As you can see there is `trxref` query parameter in the URL. This query parameter will be needed in the `/api/payment/verify` endpoint to verify payments. Once the payment is verified, the task will be created.


**Error Handling**  
If fetching Task fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request Error:** Insufficient balance/User does not have a wallet
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.









### Fetch Advert Tasks
**Endpoint:** `/api/tasks/advert`  
**HTTP Method:** `GET`  
**Description:** Retrieve all advert tasks.  

The endpoint is paginated, returning 10 advert tasks per page by default.

**Query Parameters:**
- `page` (optional): The page number to retrieve. Defaults to 1 if not provided.

This endpoint fetches all advert tasks specifically.

**Key Response Details:**

- `total` (integer): The total number of advert tasks on Trendit³.
- `advert_tasks` (list): A list containing advert tasks (up to 10 per page).
    - `creator` (object): details on the user that created the task
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve advert tasks.

**A Successful Response Example:**
```json
{
    "message": "Advert tasks fetched successfully",
    "status": "success",
    "status_code": 200,
    "total_pages": 2,
    "current_page": 1,
    "total": 15,
    "advert_tasks": [
        {
            "caption": "ujhbujnb",
            "gender": "Male",
            "hashtags": "#hjsdf, #kskj, #kslkf",
            "id": 4,
            "media_path": "https://cloudinary.com/advertisement1.png",
            "payment_status": "Complete",
            "platform": "youtube",
            "posts_count": 3,
            "target_country": "Nigeria",
            "target_state": "Lagos",
            "task_key": "leplfdrxf9",
            "type": "advert",
            "creator": {
                "email": "trendit_user@gmail.com",
                "id": 1,
                "username": "trendit_user"
            },
        }
        // ... (up to 10 tasks per page)
    ]
}
```

**To Fetch Advert Tasks from a Specific Page:**  
Include the page query parameter in the endpoint. For example, to fetch tasks from page 2, send a GET request to `/api/tasks/advert?page=2`.

**Error Handling**  
If fetching advert tasks fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.




### Fetch Advert Tasks for a Specific Platform

**Endpoint:** `/api/tasks/advert/{platform}`  
**HTTP Method:** `GET`  
**Description:** Retrieve all advert tasks for a specific platform.  

The endpoint is paginated, returning 10 tasks per page by default.

**Path Parameter:**
- `{platform}` (required): The platform for which to retrieve advert tasks, e.g., `TikTok`.

Example Request:
`GET /api/tasks/advert/TikTok`

**Key Response Details:**

- `total` (integer): The total number of advert tasks for the specified platform on Trendit³.
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve advert tasks for the specified platform.
- `advert_tasks` (list): A list containing advert tasks (up to 10 per page) for the specified platform.
    - `creator` (object): details on the user that created the task

**A Successful Response Example:**
```json
{
    "message": "All Advert Tasks for TikTok fetched successfully",
    "status": "success",
    "status_code": 200,
    "total_pages": 2,
    "current_page": 1,
    "total": 13,
    "advert_tasks": [
        {
            "caption": "ujhbujnb",
            "gender": "Male",
            "hashtags": "#hjsdf, kskj, kslkf",
            "id": 4,
            "media_path": null,
            "payment_status": "Complete",
            "platform": "TikTok",
            "posts_count": 3,
            "target_country": "Nigeria",
            "target_state": "Lagos",
            "task_key": "leplrxf9x1",
            "type": "advert",
            "creator": {
                "email": "trendit_user@gmail.com",
                "id": 1,
                "username": "trendit_user"
            },
        },
        // ... (up to 10 tasks per page)
    ]
}
```

**To Fetch Advert Tasks for TikTok from a Specific Page:**  
Include the page query parameter in the endpoint. For example, to fetch tasks from page 2, send a GET request to `/api/tasks/advert/TikTok?page=2`.

**Error Handling**  
If fetching advert tasks for the specified platform fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### Fetch Advert Tasks Grouped by Field

**Endpoint:** `/api/tasks/advert/grouped-by/{field}`  
**HTTP Method:** `GET`  
**Description:** Retrieve all advertisement tasks grouped by field.

**Path Parameter:**
- `{field}` (required): The field by which to group advert tasks, e.g., `platform` or `gender`.


**Key Response Details:**

- `tasks_grouped_by_field` (object): An object containing field values as keys, each with an associated list of advertisement tasks (`tasks`) and the total number of tasks (`total`) for that field.


**A Successful Response Example (Grouped by Platform):**
```json
{
    "message": "Advert tasks grouped by platform fetched successfully.",
    "status": "success",
    "status_code": 200,
    "tasks_by_platform": {
        "youtube": {
            "tasks": [
                {
                    "caption": "ujhbujnb",
                    "creator": {
                        "email": "trendit_user@gmail.com",
                        "id": 1,
                        "username": "trendit_user"
                    },
                    "gender": "Male",
                    "hashtags": "#hjsdf, kskj, kslkf",
                    "id": 2,
                    "media_path": null,
                    "payment_status": "Complete",
                    "platform": "youtube",
                    "posts_count": 3,
                    "target_country": "Nigeria",
                    "target_state": "Lagos",
                    "task_key": "vie26tzy0m",
                    "type": "advert"
                },
                // ... (up to 10 tasks per platform)
            ],
            "total": 3
        },
        // ... (more platforms)
    }
}
```

**Error Handling**  
If fetching advert tasks grouped by platform fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.




### Fetch Engagement Tasks
**Endpoint:** `/api/tasks/engagement`  
**HTTP Method:** `GET`  
**Description:** Retrieve all engagement tasks.  
**Query Parameters:** - `page` (optional): The page number to retrieve. Defaults to 1 if not provided.

This endpoint fetches all engagement tasks specifically.  
The tasks are paginated, returning 10 engagement tasks per page by default.



**Key Response Details:**
- `total` (integer): The total number of engagement tasks on Trendit³.
- `engagement_tasks` (list): A list containing engagement tasks (up to 10 per page).
    - `creator` (object): details on the user that created the task
- `current_page` (integer): The current page number.
- `total_pages` (integer): Total number of pages to retrieve engagement tasks.


**A Successful Response Example:**
```json
{
    "message": "All Engagement Tasks fetched successfully",
    "status": "success",
    "status_code": 200,
    "total_pages": 2,
    "current_page": 1,
    "total": 7,
    "engagement_tasks": [
        {
            "account_link": "https://hjsj.com",
            "engagements_count": 1,
            "goal": "Follow my account",
            "id": 1,
            "media_path": null,
            "payment_status": "Complete",
            "platform": "instagram",
            "task_key": "bwg2ublaxc",
            "type": "engagement"
            "creator": {
                "email": "trendit_user@gmail.com",
                "id": 1,
                "username": "trendit_user"
            },
        },
        // ... (up to 10 tasks per page)
    ]
}
```

**To Fetch Engagement Tasks from a Specific Page:**  
Include the page query parameter in the endpoint. For example, to fetch tasks from page 2, send a GET request to `/api/tasks/engagement?page=2`.

**Error Handling**  
If fetching engagement tasks fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.






### Fetch Engagement Tasks Grouped by Field

**Endpoint:** `/api/tasks/engagement/grouped-by/{field}`  
**HTTP Method:** `GET`  
**Description:** Retrieve all engagement tasks grouped by a specified field. 

**Path Parameter:**
- `{field}` (required): The field by which to group engagement tasks, e.g., `goal` or `platform`.

**Example Request:**  `GET /api/tasks/engagement/grouped-by/goal`

**Key Response Details:**

- `tasks_grouped_by_field` (object): An object containing field values as keys, each with an associated list of engagement tasks (`tasks`) and the total number of tasks (`total`) for that field.

**A Successful Response Example (Grouped by Goal):**
```json
{
    "message": "Engagement tasks grouped by goal fetched successfully.",
    "status": "success",
    "status_code": 200,
    "tasks_grouped_by_goal": {
        "Follow my account": {
            "tasks": [
                {
                    "account_link": "https://hjsj.com",
                    "creator": {
                        "email": "trendit_user@gmail.com",
                        "id": 1,
                        "username": "trendit_user"
                    },
                    // ... (task details)
                },
                // ... (up to 10 tasks for the specified goal)
            ],
            "total": 1
        },
        // ... (more goals)
    }
}
```

**Error Handling**   
If fetching engagement tasks grouped by the specified field fails, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.


***


## Tasks Performance



### Perform Task

**Endpoint:** `/api/perform-task`  
**HTTP Method:** `POST`  
**Description:** Perform a Task  
**Login Required:** True  


This endpoint aims to record Performed task in the Trendit³ database. Perfomed task can later be reviewed and approved by an admin.


**Form Data Parameters:**
- `task_id_key` (required): The ID or key of the task to be performed.
- `screenshot` (required): The screenshot as proof of task completion.
- `reward_money` (required): The amount of money to be earned for performing the task.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the task was performed successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 201).
- `performed_task` (object): An object containing details of the performed task.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Task performed successfully",
    "status_code": 201,
    "performed_task": {
        "id": 2,
        "proof_screenshot_path": "http://res.cloudinary.com/dco3/image/upload/yy0.png",
        "reward_money": 100.0,
        "status": "Pending",
        "task_id": 2,
        "task_type": "advert",
        "date_completed": "Sat, 09 Dec 2023 13:51:05 GMT",
        "user": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        }
    }
}
```

**Error Handling**  
If performing the task fails (e.g., if the required data is missing, the task does not exist, or there's an issue with the server), you will receive a JSON response with details about the error, including the status code.


- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 401 Unauthorized:** User is not logged in
- **HTTP 404 Not Found:** The requested task was not found.
- **HTTP 409 Not Found:** The task already performed by user.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.




### Fetch All Performed TaskS

**Endpoint:** `/api/performed-tasks`  
**HTTP Method:** `GET`  
**Description:** Fetch all tasks performed by the current logged-in user.  
**Login Required:** True  

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the performed tasks were fetched successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `performed_tasks` (list): A list containing details of all performed tasks by the current user.

**Note for Admins:**  
Admins can use the `/api/admin/performed-tasks` endpoint to fetch all performed tasks, regardless of the user.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Performed tasks fetched successfully",
    "status_code": 200,
    "all_performed_tasks": [
        {
            "id": 1,
            "proof_screenshot_path": "http://res.cloudinary.com/dco3/image/upload/xx0.png",
            "reward_money": 50.0,
            "status": "Completed",
            "task_id": 1,
            "task_type": "engagement",
            "date_completed": "Sat, 09 Dec 2023 14:30:00 GMT"
            "user": {
                "email": "trendit_user@gmail.com",
                "id": 1,
                "username": "trendit_user"
            }
        },
        {
            "id": 2,
            "proof_screenshot_path": "http://res.cloudinary.com/dco3/image/upload/yy0.png",
            "reward_money": 100.0,
            "status": "Pending",
            "task_id": 2,
            "task_type": "advert",
            "date_completed": "Sat, 09 Dec 2023 13:51:05 GMT"
            "user": {
                "email": "trendit_user@gmail.com",
                "id": 1,
                "username": "trendit_user"
            }
        }
    ]
}
```

**Error Handling**  
If fetching performed tasks fails (e.g., if there's an issue with the server), you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.






### Fetch Single Performed Task

**Endpoint:** `/api/performed-tasks/{performed_task_id}`  
**HTTP Method:** `GET`  
**Description:** Fetch details of a single task performed by the current logged-in user based on the task's ID.  
**Login Required:** True  

**URL Parameters:**
- `{performed_task_id}` (integer, required): The ID of the performed task to be fetched.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the performed task was fetched successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `performed_task` (object): An object containing details of the performed task.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Task performed by the current user fetched successfully",
    "status_code": 200,
    "performed_task": {
        "date_completed": "Sat, 09 Dec 2023 13:53:51 GMT",
        "id": 3,
        "proof_screenshot_path": "http://res.cloudinary.com/dc3/image/upload/v1/q7v.png",
        "reward_money": 100.0,
        "status": "Pending",
        "task_id": 2,
        "task_type": "advert",
        "user": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        }
    }
}
```

**Error Handling**  
If fetching the single performed task fails (e.g., if the task does not exist or there's an issue with the server), you will receive a JSON response with details about the error, including the status code.

- **HTTP 401 Unauthorized:** User is not logged in
- **HTTP 404 Not Found:** The requested performed task was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### Update Performed Task

**Endpoint:** `/api/performed-tasks/{performed_task_id}`  
**HTTP Method:** `PUT`  
**Description:** Update details of a single task performed by the current logged-in user.  
**Login Required:** True  

**URL Parameters:**
- `{performed_task_id}` (integer, required): The ID of the performed task to be updated.

**Form Data Parameters:**
- `status` (optional): The status of the performed task (e.g., "Completed" or "Pending").
- `reward_money` (optional): The updated amount of money earned for performing the task.
- `proof_screenshot` (optional): The updated screenshot as proof of task completion.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the performed task was updated successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `performed_task` (object): An object containing details of the updated performed task.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Performed task updated successfully",
    "status_code": 200,
    "performed_task": {
        "date_completed": "Sat, 09 Dec 2023 13:53:51 GMT",
        "id": 3,
        "proof_screenshot_path": "http://res.cloudinary.com/dcozguaw3/image/upload/v1702130032/2023/12/mts-icon-6q7v.png",
        "reward_money": 150.0,
        "status": "Completed",
        "task_id": 2,
        "task_type": "advert",
        "user": {
            "email": "trendit_user@gmail.com",
            "id": 1,
            "username": "trendit_user"
        }
    }
}
```

**Error Handling**  
If updating the performed task fails (e.g., if the task does not exist, validation error, or there's an issue with the server), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 401 Unauthorized:** User is not logged in
- **HTTP 404 Not Found:** The requested performed task was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.



### Delete Performed Task

**Endpoint:** `/api/performed-tasks/{performed_task_id}`  
**HTTP Method:** `DELETE`  
**Description:** Delete a single performed task by the current logged-in user.  
**Login Required:** True  

**URL Parameters:**
- `{performed_task_id}` (integer, required): The ID of the performed task to be deleted.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the performed task was deleted successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Performed task deleted successfully",
    "status_code": 200
}
```
**Error Handling**  
If deleting the performed task fails (e.g., if the task does not exist or there's an issue with the server), you will receive a JSON response with details about the error, including the status code.

- **HTTP 404 Not Found:** The requested performed task was not found.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

***
## Pofile

### Get User Profile

**Endpoint:** `/api/profile`  
**HTTP Method:** `GET`  
**Description:** Fetch the profile details of the current logged-in user.  
**Login Required:** True

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the user profile was fetched successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `user_profile` (object): An object containing details of the user's profile.

**User Profile Object:**
- `id` (integer): The unique identifier of the user.
- `username` (string): The username of the user.
- `email` (string): The email address of the user.
- `firstname` (string): The first name of the user.
- `lastname` (string): The last name of the user.
- `gender` (string): The gender of the user.
- `country` (string): The country of residence of the user.
- `state` (string): The state of residence of the user.
- `local_government` (string): The local government area of residence of the user.
- `date_joined` (string): The date and time when the user joined the platform.
- `profile_picture` (string): The URL of the user's profile picture.
- `referral_link` (string): The referral link associated with the user.
- `wallet` (object): An object containing details of the user's wallet.
    - `balance` (float): The current balance in the user's wallet.
    - `currency_code` (string): The currency code (e.g., "NGN").
    - `currency_name` (string): The currency name (e.g., "Nigerian naira").

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "User profile fetched successfully",
    "status_code": 200,
    "user_profile": {
        "id": 1,
        "username": "trendit_user",
        "email": "trendit_user@gmail.com",
        "firstname": "",
        "lastname": "",
        "gender": "Male",
        "country": "Nigeria",
        "state": "Lagos",
        "local_government": "Alimosho",
        "date_joined": "Fri, 24 Nov 2023 21:43:24 GMT",
        "profile_picture": "",
        "referral_link": "",
        "wallet": {
            "balance": 923.0,
            "currency_code": "NGN",
            "currency_name": "Nigerian naira"
        }
    }
}
```
**Error Handling**  
If fetching the user profile fails (e.g., if there's an issue with the server), you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.






### Edit User Profile

**Endpoint:** `/api/profile/edit`  
**HTTP Method:** `PUT`  
**Description:** Update the profile details of the current logged-in user.  
**Login Required:** True  

**Form Data Parameters (optional):**
- `firstname` (string): The updated first name of the user.
- `lastname` (string): The updated last name of the user.
- `username` (string): The updated username of the user.
- `gender` (string): The updated gender of the user.
- `country` (string): The updated country of residence of the user.
- `state` (string): The updated state of residence of the user.
- `local_government` (string): The updated local government area of residence of the user.
- `profile_picture` (binary data, optional): The updated profile picture of the user.


**Note:** Each parameter is optional, and you only need to include the ones that require an update. If a parameter is not included, the corresponding information will remain unchanged.


**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the user profile was updated successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `user_profile` (object): An object containing details of the updated user profile.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "User profile updated successfully",
    "status_code": 200,
    "user_profile": {
        "id": 1,
        "username": "new_trendit_user",
        "email": "trendit_user@gmail.com",
        "firstname": "trendit",
        "lastname": "new user",
        "gender": "Male",
        "country": "Nigeria",
        "state": "Lagos",
        "local_government": "Alimosho",
        "date_joined": "Sat, 09 Dec 2023 12:28:06 GMT",
        "profile_picture": "http://res.cloudinary.com/dc/image/upload/vk0.png",
        "referral_link": null
    }
}
```

**Error Handling**  
If updating the user profile fails (e.g., if there's an issue with the server or validation error), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Validation error or invalid input data.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.






### Fetch User Profile Picture

**Endpoint:** `/api/profile-pic`  
**HTTP Method:** `GET`  
**Description:** Retrieve the profile picture of the current logged-in user.  
**Login Required:** True  

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the profile picture was fetched successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `profile_pic` (string): The URL of the user's profile picture.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Profile picture fetched successfully",
    "status_code": 200,
    "profile_pic": "http://res.cloudinary.com/dco/image/upload/v1/0nk0.png"
}
```
**Error Handling**  
If fetching the profile picture fails (e.g., if there's an issue with the server or the user does not have a profile picture), you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.




### Edit User Profile Picture

**Endpoint:** `/api/profile-pic/edit`  
**HTTP Method:** `PUT`  
**Description:** Update the profile picture of the current logged-in user.  
**Login Required:** True  

**Form Data Parameters:**
- `profile_picture` (binary data): The updated profile picture of the user.

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the user's profile picture was updated successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `profile_pic` (string): The URL of the user's profile picture.

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Profile picture updated successfully",
    "status_code": 200
    "profile_pic": "http://res.cloudinary.com/dco/image/upload/v1/0nk0.png"
}
```

**Error Handling**  
If updating the profile picture fails (e.g., if there's an issue with the server or invalid input data), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Invalid input data.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.





### Edit User Email
**Endpoint:** `/api/profile/email-edit`  
**HTTP Method:** `POST`  
**Description:** Initiate the process to update the user's email. A verification code will be sent to the new email.  
**Login Required:** True  

**Request Body:**
```json
{
    "new_email": "new_trendit_user@gmail.com"
}

```

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the verification code was sent successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `edit_email_token` (string): A token that will be used to verify and complete the email update process.


**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Verification code sent successfully",
    "status_code": 200,
    "edit_email_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
}
```

**Error Handling**  
If request, you will receive a JSON response with details about the error, including the status code.

- **HTTP 406 Not Acceptable:** email provided isn't a new email
- **HTTP 409 Conflict:** User with the same email already exists.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.


### Verify and Update User Email
**Endpoint:** `/api/profile/email-verify`  
**HTTP Method:** `POST`  
**Description:** Verify the provided verification code and update the user's email.  
**Login Required:** True  


**Request Body:**
```json
{
    "entered_code": 688900,
    "edit_email_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
}
```

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the user's email was updated successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Email updated successfully",
    "status_code": 200,
    "user_email": "new_trendit@gmail.com"
}
```

**Error Handling**  
If verification fails (e.g., incorrect verification code), you will receive a JSON response with details about the error, including the status code.

- **HTTP 400 Bad Request:** Invalid input data or Verification code is incorrect.
- **HTTP 500 Internal Server Error:** An error occurred while processing the request.











### Resend Verification Code Request
**Endpoint:** `/api/resend-code`  
**HTTP Method:** `POST`  
**Description:** Initiate the process to update the user's email. A verification code will be sent to the new email.  
**Login Required:** True  

**Query Parameters:**

- `code_type` (string): The type of operation for which the verification code should be resent. Options include email-edit.


**Request Body:**
```json
{
    "new_email": "new_trendit_user@gmail.com"
}

```

**Example Request for Resending Verification Code:**  `GET /api/resend-code?code_type=email-edit`

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the verification code was resent successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `edit_email_token` (string): A new token that will be used for the verification process.


**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Verification code sent successfully",
    "status_code": 200,
    "edit_email_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
}
```

**Error Handling**  
If there is an issue with resending the verification code, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

***
## Referral System

The Trendit³ platform includes a referrer system, allowing users to refer others to the platform. Each referrer has a unique code associated with their account, which is appended to the signup URL. Frontend developers are responsible for extracting this code and including it as a query parameter when making the signup API request.


### Generate Referral Link

**Endpoint:** `/api/referral/generate-link`  
**HTTP Method:** `GET`  
**Description:** Generate a unique referral link for the current logged-in user.  
**Login Required:** True

**Key Response Details:**

- `status` (string): The status of the request, e.g., "success."
- `message` (string): A success message indicating that the referral link was generated successfully.
- `status_code` (integer): The HTTP status code indicating the success of the request (e.g., 200).
- `referral_link` (string): The unique referral link associated with the current logged-in user.


**A Successful Response Example:**
```JSON
{
    "status": "success",
    "message": "Referral link generated successfully",
    "status_code": 200,
    "referral_link": "www.trendit3.com/signup/oe9uw83k"
}
```

**Error Handling**  
If there is an issue with generating the referral link, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.




### Fetch Referral History

**Endpoint:** `/api/referral/history`  
**HTTP Method:** `GET`  
**Description:** Fetch the referral history for the current logged-in user.  
**Query Parameters:** `page` - The page number to retrieve. It Defaults to 1 if not provided.  
**Login Required:** True

**Key Response Details:**

- `total`  (integer): The total number of referral records for the user.
- `total_pages` (integer): The total number of pages available based on the pagination.
- `current_page` (integer): The current page number.
- `referral_history` (list): A list containing referral history records.
    - `id` (integer): The unique identifier for the referral history record.
    - `referrer_id` (integer): The user ID of the referrer.
    - `status` (string): The status of the referral, e.g., "Registered, Pending."
    - `username` (string): The username of the referred user.
    - `date` (string): The date and time when the referral occurred.

**Pagination:**  
This endpoint is paginated, returning 10 referral history records per page.  
To access other pages, include the page parameter in the request, e.g., `?page=2`.
The default page is 1 if not provided.

**Example Request for Fetching Referral History:**   
`GET /api/referral/history?page=1`

**A Successful Response Example:**
```json
{
    "status": "success",
    "message": "Referral history fetched successfully",
    "status_code": 200,
    "total": 20,
    "total_pages": 2,
    "current_page": 1,
    "referral_history": [
        {
            "date": "Sun, 10 Dec 2023 21:35:16 GMT",
            "id": 1,
            "referrer_id": 1,
            "status": "Registered",
            "username": "a_trendit_user"
        },
        // ... (records for page 1 up to 10)
    ]
}

```

**Error Handling**  
If there is an issue with fetching the referral history, you will receive a JSON response with details about the error, including the status code.

- **HTTP 500 Internal Server Error:** An error occurred while processing the request.

***