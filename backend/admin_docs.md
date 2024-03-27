```markdown
# Trendit3 Admin API Documentation

Welcome to the Trendit3 Admin API documentation. This guide provides detailed information on how to interact with the admin endpoints of the Trendit3 platform. Ensure you have the necessary permissions to access these endpoints.

## Base URL

All URLs referenced in the documentation have the following base:

```
https://api.trendit3.com/api/admin/
```

## Authentication

Please note that accessing the admin endpoints requires proper authentication. Ensure you include your authentication token in the header of your requests.

---

## Endpoints

### Dashboard Data

- **Path:** `/dashboard_data`
- **Method:** POST
- **Description:** Retrieves summary data for the dashboard, including payments and payouts.
- **Sample Response:**

```json
{
    "total_received_payments": 5000.0,
    "total_payouts": 3000.0,
    "received_payments_per_month": {
        "2023-01": 2000.0,
        "2023-02": 1500.0,
        "2023-03": 1500.0
    },
    "payouts_per_month": {
        "2023-01": 1000.0,
        "2023-02": 1000.0,
        "2023-03": 1000.0
    },
    "payment_activities_per_month": {
        "2023-01": 3,
        "2023-02": 2,
        "2023-03": 2
    }
}
```

### Users - Get All Users

- **Path:** `/users`
- **Method:** POST
- **Description:** Fetches all users registered on the platform.
- **Sample Response:**

```json
{
    "message": "All users fetched successfully",
    "status": "success",
    "status_code": 200,
    "total": 2,
    "users": [
        {
            "birthday": "Mon, 02 Jan 1989 00:00:00 GMT",
            "country": "South Africa",
            ...
            "wallet": {
                "balance": 2650.0,
                "currency_code": "ZAR",
                "currency_name": "South African rand"
            }
        },
        {
            "birthday": "Mon, 10 Mar 1997 00:00:00 GMT",
            "country": "Nigeria",
            ...
            "wallet": {
                "balance": 50.0,
                "currency_code": "NGN",
                "currency_name": "Nigerian naira"
            }
        }
    ]
}
```

### User - Get a Single User

- **Path:** `/users/{id}`
- **Method:** POST
- **Description:** Retrieves details for a single user by their ID.
- **Sample Response:**

```json
{
    "message": "User fetched successfully",
    "status": "success",
    "status_code": 200,
    "user": {
        "birthday": null,
        "country": null,
        ...
        "wallet": {
            "balance": 0.0,
            "currency_code": "USD",
            "currency_name": "Dollars"
        }
    }
}
```

### Tasks - Get All Tasks

- **Path:** `/tasks`
- **Method:** POST
- **Description:** Fetches all tasks created on the platform.
- **Sample Response:**

```json
{
    "message": "All tasks fetched successfully",
    "status": "success",
    "status_code": 200,
    "tasks": [
        {
            "account_link": "https://github.com/osomhe1",
            ...
            "updated_at": "Wed, 20 Mar 2024 21:54:10 GMT"
        }
    ],
    "total": 1
}
```

### Approve Task

- **Path:** `/approve-task/{id}`
- **Method:** POST
- **Description:** Approves a task by its ID.
- **Sample Response:**

```json
{
    "message": "Task approved successfully",
    "status": "success",
    "status_code": 200
}
```

### Reject Task

- **Path:** `/reject-task/{id}`
- **Method:** POST
- **Description:** Rejects a task by its ID.
- **Sample Response:**

```json
{
    "message": "Task rejected successfully",
    "status": "success",
    "status_code": 200
}
```

### Review Task

- **Path:** `/tasks/{id}`
- **Method:** POST
- **Description:** Retrieves details for reviewing a task by its ID.
- **Sample Response:**

```json
{
    "message": "Task fetched successfully",
    "status": "success",
    "status_code": 200,
    "task": {
        "account_link": "https://github.com/osomhe1",
        ...
        "updated_at": "Thu, 21 Mar 2024 07:48:58 GMT"
    }
}
```

---

For any issues or further assistance, please contact the Trendit3 support team.
