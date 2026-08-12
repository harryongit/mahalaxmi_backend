# MahalaxmiPuja API Sheet

Base URL: `http://localhost:8000/api/v1`

### Schema Data Types

| Type | Format |
|------|--------|
| amounts | stored in **paise** (e.g., 1000 = INR 10.00) |
| dates | ISO 8601 string: `"2024-01-15T10:30:00Z"` |
| dates (no time) | ISO 8601 date: `"2024-01-15"` |
| booleans | `true` / `false` |

### Enums

| Enum | Values |
|------|--------|
| `GanEnum` | `Rakshasa`, `Manushya`, `Deva` |
| `OrderStatus` | `PENDING`, `CONFIRMED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| `PaymentStatus` | `PENDING`, `PAID`, `FAILED`, `REFUNDED` |
| `PaymentVerificationSource` | `FRONTEND_VERIFIED`, `WEBHOOK_VERIFIED`, `MANUAL_VERIFIED` |
| `EnquiryStatus` | `OPEN`, `IN_PROGRESS`, `RESOLVED` |

### Common Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid input / Validation error |
| 401 | Authentication required |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## 1. AUTH (Public)

### 1.1 Request OTP
- **URL**: `POST /auth/otp/request`

<details>
<summary><b>Request</b></summary>

```json
{
  "phone_number": "+919876543210"
}
```

</details>
<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "OTP sent successfully."
}
```

</details>
<details>
<summary><b>Response (429)</b></summary>

```json
{
  "detail": "Too many OTP requests. Try again later."
}
```
</details>

---

### 1.2 Verify OTP & Login/Register
- **URL**: `POST /auth/otp/verify`

<details>
<summary><b>Request</b></summary>

```json
{
  "phone_number": "+919876543210",
  "otp": "483920"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
</details>

---

### 1.3 Refresh Token
- **URL**: `POST /auth/refresh`

<details>
<summary><b>Request</b></summary>

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_manager": "bearer"
}
```
</details>
<details>
<summary><b>Response (403)</b></summary>

```json
{
  "detail": "Invalid or expired refresh token"
}
```
</details>

---

## 2. USERS (Auth required)

Use header `Authorization: Bearer <access_token>` for all endpoints in this section.

### 2.1 Get Current User
- **URL**: `GET /users/me`

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "+919876543210",
  "gotra": null,
  "gan": null,
  "address": null,
  "city": null,
  "state": null,
  "pin_code": null,
  "country": null,
  "whatsapp_opt_in": false,
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```
</details>

---

### 2.2 Update Current User
- **URL**: `PUT /users/me`

<details>
<summary><b>Request</b></summary>

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "gotra": "Kashyapa",
  "gan": "Manushya",
  "address": "123 Temple Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pin_code": "400001",
  "country": "India",
  "whatsapp_opt_in": true
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

Same as Get Current User response.

</details>

---

### 2.3 Get User Stats
- **URL**: `GET /users/me/stats`

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "total_orders": 5,
  "completed_orders": 3,
  "active_orders": 1,
  "total_spent": 6200
}
```
</details>

---

## 3. SERVICES

### 3.1 List Services
- **URL**: `GET /services/?category_id=1&is_active=true`

Query Parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category_id` | int | none | Filter by category |
| `is_active` | bool | true | Filter by active status |

<details>
<summary><b>Response (200)</b></summary>

```json
[
  {
    "id": 1,
    "name": "Lakshmi Puja",
    "slug": "lakshmi-puja",
    "category_id": 1,
    "description": "Puja for Goddess Lakshmi",
    "short_description": "Wealth & prosperity puja",
    "price": 1100,
    "is_custom_amount": false,
    "min_amount": null,
    "active_from": null,
    "active_to": null,
    "is_active": true,
    "display_order": 0,
    "icon": "\U0001f414",
    "inclusions": "Sankalp, 108 names recitation, aarti, prasad",
    "created_at": "2024-01-15T10:30:00Z",
    "category": {
      "id": 1,
      "name": "Puja",
      "slug": "puja",
      "description": "Sacred puja ceremonies"
    },
    "festivals": [
      {
        "id": 1,
        "name": "Diwali"
      }
    ]
  }
]
```
</details>

---

### 3.2 Get Service by ID
- **URL**: `GET /services/{id}`

<details>
<summary><b>Response (200)</b></summary>

Same as single object above.

</details>

---

### 3.3 Create Service (Admin)
- **URL**: `POST /services/`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "name": "Lakshmi Puja",
  "slug": "lakshmi-puja",
  "category_id": 1,
  "description": "Puja for Goddess Lakshmi",
  "short_description": "Wealth & prosperity",
  "price": 1100,
  "is_custom_amount": false,
  "min_amount": null,
  "active_from": null,
  "active_to": null,
  "is_active": true,
  "display_order": 0,
  "icon": "\U0001f414",
  "inclusions": "Sankalp, 108 names recitation, aarti, prasad",
  "festival_ids": [1, 2]
}
```
</details>

<details>
<summary><b>Response (201)</b></summary>

Same as single service object above.

</details>

---

### 3.4 Update Service (Admin)
- **URL**: `PUT /services/{id}`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

Partial or full fields:

```json
{
  "name": "Updated Name",
  "category_id": 2,
  "is_active": false,
  "festival_ids": [1]
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

Updated service object.

</details>

---

### 3.5 Delete Service (Admin)
- **URL**: `DELETE /services/{id}`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "Service deleted successfully"
}
```
</details>

---

### 3.6 List Categories
- **URL**: `GET /services/categories/`

<details>
<summary><b>Response (200)</b></summary>

```json
[
  {
    "id": 1,
    "name": "Puja",
    "slud": "puja",
    "description": "Sacred puja ceremonies"
  }
]
```
</details>

---

## 4. ORDERS (Auth required)

### 4.1 Create Order

- **URL**: `POST /orders/`

<details>
<summary><b>Request</b></summary>

```json
{
  "items": [
    {
      "service_id": 1,
      "devotee_name": "Rahul",
      "gotra": "Kasyapa",
      "scheduled_date": null,
      "amount": 1100
    }
  ],
  "notes": "Please perform in the morning"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "id": 1,
  "order_id": "MLX-20240115-AB12",
  "user_id": 1,
  "status": "PENDING",
  "payment_status": "PENDING",
  "total_amount": 1100,
  "notes": "Please perform in the morning",
  "booking_date": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "items": [
    {
      "id": 1,
      "service_id": 1,
      "devotee_name": "Rahul",
      "gotra": "Kasyapa",
      "scheduled_date": null,
      "amount": 1100,
      "status": "PENDING",
      "service": {
        "id": 1,
        "name": "Lakshmi Puja",
        ... // full service object
      }
    }
  ]
}
```
</details>

---

### 4.2 List user's orders
- **URL**: `GET /orders/`

<details>
<summary><b>Response (200)</b></summary>

```json
[
  { ... // order object },
  { ... // order object }
]
```
</details>

---

### 4.3 Get order detail
- **URL**: `GET /orders/{order_id}`

| Param | Type | Description |
|-------|------|-------------|
| `order_id` | string | The MLX-XXXXXX-XXXX order identifier |

<details>
<summary><b>Response (200)</b></summary>

Full order object with items and services.

</details>

---

### 4.4 Cancel order
- **URL**: `PATCH /orders/{order_id}/cancel`

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "Order cancelled successfully"
}
```
</details>

<details>
<summary><b>Response (400)</b></summary>

```json
{
  "detail": "Only pending orders can be cancelled"
}
```
</details>

---

### 4.5 Download Invoice (paid orders)
- **URL**: `GET /orders/{order_id}/invoice`

<details>
<summary><b>Response (200)</b></summary>

Returns a PDF file download (`Invoice_MLX-20241015-XXXX.pdf`).

</details>

---

### 4.6 Admin: List all orders
- **URL**: `GET /orders/admin/list`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

Array of all orders with items.

</details>

---

### 4.7 Admin: Update order status
- **URL**: `PATCH /orders/admin/{order_id}/status`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "status": "CONFIRMED",
  "payment_status": null
}
```
or
```json
{
  "status": "COMPLETED",
  "payment_status": "PAID"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

Updated order object.

</details>

---

## 5. PAYMENTS

### 5.1 Create Payment Order (Razorpay)
- **URL**: `POST /payments/create-order`

<details>
<summary><b>Request</b></summary>

```json
{
  "order_id": 1
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "id": 1,
  "order_id": 1,
  "razorpay_order_id": "order_Oi8s4wTAQtk4J0",
  "razorpay_payment_id": null,
  "amount": 1100,
  "status": "PENDING",
  "verification_source": null,
  "payment_method": null,
  "created_at": "2024-09-20T10:00:00Z",
  "payment_date": null
}
```
</details>

---

### 5.2 Verify Payment
- **URL**: `POST /payments/verify`

<details>
<summary><b>Request</b></summary>

```json
{
  "razorpay_order_id": "order_Oi8s4wTAQtk4J0",
  "razorpay_payment_id": "pay_Oi8s6hBQsBqCa2",
  "razorpay_signature": "0a6c753e3d8fc1a1b34281a51981468e3d1d4de9c195485e0fb0c5154e4d3e6f"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "Payment verified successfully"
}
```
</details>

---

### 5.3 Razorpay Webhook
- **URL**: `POST /payments/webhook`

This endpoint is called by Razorpay, not directly. Requires a valid Razorpay webhook signature.

<details>
<summary><b>Request</b></summary>

```json
{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_Oi8s6hBQsBqCa2",
        "order_id": "order_Oi8s4wTAQtk4J0",
        "amount": 1100,
        "currency": "INR",
        "status": "captured"
      }
    }
  }
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "status": "ok"
}
```
</details>

---

### 5.4 Admin: Refund payment
- **URL**: `POST /payments/admin/{id}/refund`
- **Header**: `Authorization: Bearer <admin_access_token>`

| Param | Type | Description |
|-------|------|-------------|
| `id` | int | Payment record ID |

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "Refund processed successfully",
  "refund_id": "rfnd_OiSG7B2G7sxIQa"
}
```
</details>

---

## 6. ENQUIRIES

### 6.1 Create enquiry
- **URL**: `POST /enquiries/`
- **Auth**: None

<details>
<summary><b>Request</b></summary>

```json
{
  "name": "Rahul",
  "email": "rahul@example.com",
  "phone": "+911234567890",
  "subject": "Puja Booking",
  "message": "I would like to book a Lakshmi Puja for Navratri"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "id": 1,
  "name": "Rahul",
  "email": "rahul@example.com",
  "phone": "+911234567890",
  "subject": "Puja Booking",
  "message": "I would like to book a Lakshmi Puja for Navratri",
  "status": "OPEN",
  "admin_reply": null,
  "created_at": "2024-09-20T10:00:00Z",
  "updated_at": null
}
```
</details>

---

### 6.2 Admin: List enquiries
- **URL**: `GET /enquiries/admin?status=OPEN`
- **Header**: `Authorization: Bearer <admin_access_token>`

Query Parameters:
| Param | Type | Default |
|-------|------|---------|
| status | EnquiryStatus | OPEN |

<details>
<summary><b>Response (200)</b></summary>

```json
[
  {
    "id": 1,
    ...
    "status": "OPEN"
  }
]
```
</details>

---

### 6.3 Admin: Respond to enquiry
- **URL**: `PATCH /enquiries/admin/{id}/respond`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "admin_reply": "Thank you for your enquiry. We will get back to you shortly."
}
```

</details>

<details>
<summary><b>Response (200)</b></summary>

Full enquiry object with status changed to `RESOLVED` and `admin_reply` filled.

</details>

---

### 6.4 Admin: Update enquiry status
- **URL**: `PATCH /enquiries/admin/{id}/status`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "status": "IN_PROGRESS"
}
```
</details>

<details>
<summary><b>Overall Response (200)</b></summary>

Updated enquiry object.

</details>

---

## 7. ADMIN AUTH (Public)

### 7.1 Admin login

- **URL**: `POST /admin/auth/login`

<details>
<summary><b>Request</b></summary>

```json
{
  "email": "admin@mahalaxmipuja.com",
  "password": "admin123"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "2FA OTP sent",
  "admin_id": 1
}
```
</details>

<details>
<summary><b>Response (429)</b></summary>

```json
{
  "detail": "Too many failed login attempts. Account locked for 15 minutes."
}
```
</details>

---

### 7.2 Admin verify 2FA

- **URL**: `POST /admin/auth/verify-2fa`

<details>
<summary><b>Request</b></summary>

```json
{
  "admin_id": 1,
  "otp": "483920"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
</details>

---

## 8. ADMIN DASHBOARD

### 8.1 Get summary
- **URL**: `GET /admin/dashboard/summary`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "total_users": 42,
  "total_orders": 15,
  "total_revenue": 16500,
  "today_bookings": 3,
  "today_revenue": 3300
}
```
</details>

---

### 8.2 Recent orders (last 10)
- **URL**: `GET /admin/dashboard/recent-orders`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

Array of the 10 most recent order objects.

</details>

---

### 8.3 Recent payments (last 10)
- **URL**: `GET /admin/dashboard/recent-payments`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

Array of the 10 most recent payment objects.

</details>

---

## 9. ADMIN USERS

### 9.1 List all users
- **URL**: `GET /admin/users/`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

```json
[
  {
    "id": 1,
    "first_name": "John",
    ...
  }
]
```
</details>

---

### 9.2 Get user by ID
- **URL**: `GET /admin/users/{id}`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Response (200)</b></summary>

Full user object.

</details>

---

### 9.3 Create admin user
- **URL**: `POST /admin/users/`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "phone_number": "+919999999999",
  "email": "newadmin@example.com",
  "password": "securepassword",
  "first_name": "New",
  "last_name": "Admin"
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

Full User JSON (will have `is_admin: true`)
</details>

---

### 9.4 Update user active status
- **URL**: `PATCH /admin/users/{id}/status`
- **Header**: `Authorization: Bearer <admin_access_token>`

<details>
<summary><b>Request</b></summary>

```json
{
  "is_active": false
}
```
</details>

<details>
<summary><b>Response (200)</b></summary>

Updated user object.

</details>

---

## 10. MISC

### 10.1 Root
- **URL**: `GET /`
- **Auth**: None

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "message": "Welcome to MahalaxmiPuja.com API"
}
```
</details>

### 10.2 Health
- **URL**: `GET /health`
- **Auth**: None

<details>
<summary><b>Response (200)</b></summary>

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```
</details>

---

## Postman Testing Instructions

1. **Create a Collection** named `MahalaxmiPuja API`.

2. **Variables**: Set collection variables:

| Variable | Initial Value |
|----------|---------------|
| `base_url` | `http://localhost:8000/api/v1` |
| `access_token` | (empty) |
| `refresh_token` | (empty) |

3. **Authorization**: For Bearer-token endpoints, add an Authorization header: `Bearer {{access_token}}`.

4. **Testing Flow**:
   - Step 1: Request an OTP (use a valid phone number in dev OTP will be mocked)
   - Step 2: Look up the OTP from the backend output logs (the server will log it)
   - Step 3: Verify the OTP; capture `access_token` and `refresh_token`
   - Step 4: Use `access_token` for all authed endpoints

5. **Admin Flow**:
   - Seed an admin first: `python -m scripts.seed`
   - Login via `/admin/auth/login`
   - Find the OTP in the server logs
   - Complete 2FA with `/admin/auth/verify-2fa`


Sr. No.	API Name	Method	Full API URL	Authentication	Request Body	Success Response	Error Response
1	Request OTP	POST	http://localhost:8000/api/v1/auth/otp/request	No	json { "phone_number": "+919876543210" }	json { "message": "OTP sent successfully." }	429 json { "detail": "Too many OTP requests. Try again later." }
2	Verify OTP & Login/Register	POST	http://localhost:8000/api/v1/auth/otp/verify	No	json { "phone_number": "+919876543210", "otp": "483920" }	json { "access_token": "eyJhbGciOiJIUzI1NiIs...", "refresh_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }	Not specified
3	Refresh Token	POST	http://localhost:8000/api/v1/auth/refresh	No	json { "refresh_token": "eyJhbGciOiJIUzI1NiIs..." }	json { "access_token": "eyJhbGciOiJIUzI1NiIs...", "refresh_token": "eyJhbGciOiJIUzI1NiIs...", "token_manager": "bearer" }	403 json { "detail": "Invalid or expired refresh token" }
4	Get Current User	GET	http://localhost:8000/api/v1/users/me	Bearer Access Token	None	json { "id":1,"first_name":"John","last_name":"Doe","email":"john@example.com","phone_number":"+919876543210","gotra":null,"gan":null,"address":null,"city":null,"state":null,"pin_code":null,"country":null,"whatsapp_opt_in":false,"is_active":true,"is_admin":false,"created_at":"2024-01-15T10:30:00Z","updated_at":null }	Standard auth errors (401/403)
5	Update Current User	PUT	http://localhost:8000/api/v1/users/me	Bearer Access Token	json { "first_name":"John","last_name":"Doe","email":"john@example.com","gotra":"Kashyapa","gan":"Manushya","address":"123 Temple Street","city":"Mumbai","state":"Maharashtra","pin_code":"400001","country":"India","whatsapp_opt_in":true }	Same response as Get Current User	Validation/Auth errors
6	Get User Stats	GET	http://localhost:8000/api/v1/users/me/stats	Bearer Access Token	None	json { "total_orders":5,"completed_orders":3,"active_orders":1,"total_spent":6200 }	Standard auth errors
7	List Services	GET	http://localhost:8000/api/v1/services/?category_id=1&is_active=true	No	Query Parameters: category_id=1, is_active=true	Returns an array of service objects including category and festivals. Example: json [ { "id":1,"name":"Lakshmi Puja","slug":"lakshmi-puja","category_id":1,"description":"Puja for Goddess Lakshmi","short_description":"Wealth & prosperity puja","price":1100,"is_custom_amount":false,"min_amount":null,"active_from":null,"active_to":null,"is_active":true,"display_order":0,"icon":"🐔","inclusions":"Sankalp, 108 names recitation, aarti, prasad","created_at":"2024-01-15T10:30:00Z","category":{"id":1,"name":"Puja","slug":"puja","description":"Sacred puja ceremonies"},"festivals":[{"id":1,"name":"Diwali"}] } ]	None specified
8	Get Service by ID	GET	http://localhost:8000/api/v1/services/{id}	No	Path Parameter: id	Same single service object as above	404 if service not found
9	Create Service (Admin)	POST	http://localhost:8000/api/v1/services/	Bearer Admin Access Token	json { "name":"Lakshmi Puja","slug":"lakshmi-puja","category_id":1,"description":"Puja for Goddess Lakshmi","short_description":"Wealth & prosperity","price":1100,"is_custom_amount":false,"min_amount":null,"active_from":null,"active_to":null,"is_active":true,"display_order":0,"icon":"🐔","inclusions":"Sankalp, 108 names recitation, aarti, prasad","festival_ids":[1,2] }	Returns the created service object	Validation/Auth errors
10	Update Service (Admin)	PUT	http://localhost:8000/api/v1/services/{id}	Bearer Admin Access Token	json { "name":"Updated Name","category_id":2,"is_active":false,"festival_ids":[1] }	Returns the updated service object	Validation/Auth errors
11	Delete Service (Admin)	DELETE	http://localhost:8000/api/v1/services/{id}	Bearer Admin Access Token	None	json { "message": "Service deleted successfully" }	401 / 403 / 404
12	List Categories	GET	http://localhost:8000/api/v1/services/categories/	No	None	json [ { "id":1, "name":"Puja", "slug":"puja", "description":"Sacred puja ceremonies" } ]	None specified
13	Create Order	POST	http://localhost:8000/api/v1/orders/	Bearer Access Token	json { "items":[ { "service_id":1, "devotee_name":"Rahul", "gotra":"Kasyapa", "scheduled_date":null, "amount":1100 } ], "notes":"Please perform in the morning" }	json { "id":1, "order_id":"MLX-20240115-AB12", "user_id":1, "status":"PENDING", "payment_status":"PENDING", "total_amount":1100, "notes":"Please perform in the morning", "booking_date":"2024-01-15T10:30:00Z", "created_at":"2024-01-15T10:30:00Z", "items":[ { "id":1, "service_id":1, "devotee_name":"Rahul", "gotra":"Kasyapa", "scheduled_date":null, "amount":1100, "status":"PENDING", "service":{ "id":1, "name":"Lakshmi Puja", "...":"Full Service Object" } } ] }	Validation/Auth errors
14	List User Orders	GET	http://localhost:8000/api/v1/orders/	Bearer Access Token	None	json [ { ...Order Object... }, { ...Order Object... } ]	401 / 403
15	Get Order Details	GET	http://localhost:8000/api/v1/orders/{order_id}	Bearer Access Token	Path Parameter: order_id	Complete Order Object with all order items and service details	404 if order not found
16	Cancel Order	PATCH	http://localhost:8000/api/v1/orders/{order_id}/cancel	Bearer Access Token	None	json { "message":"Order cancelled successfully" }	400 json { "detail":"Only pending orders can be cancelled" }
							
17	Download Invoice	GET	http://localhost:8000/api/v1/orders/{order_id}/invoice	Bearer Access Token	Path Parameter: order_id	Returns PDF file Invoice_MLX-20241015-XXXX.pdf	404 / Unauthorized
18	Admin - List All Orders	GET	http://localhost:8000/api/v1/orders/admin/list	Bearer Admin Access Token	None	Array containing all order objects with items	401 / 403
19	Admin - Update Order Status	PATCH	http://localhost:8000/api/v1/orders/admin/{order_id}/status	Bearer Admin Access Token	Example 1: json { "status":"CONFIRMED", "payment_status":null } Example 2: json { "status":"COMPLETED", "payment_status":"PAID" }	Updated Order Object	Validation/Auth errors
20	Create Payment Order (Razorpay)	POST	http://localhost:8000/api/v1/payments/create-order	Bearer Access Token	json { "order_id":1 }	json { "id":1, "order_id":1, "razorpay_order_id":"order_Oi8s4wTAQtk4J0", "razorpay_payment_id":null, "amount":1100, "status":"PENDING", "verification_source":null, "payment_method":null, "created_at":"2024-09-20T10:00:00Z", "payment_date":null }	Validation/Auth errors
21	Verify Payment	POST	http://localhost:8000/api/v1/payments/verify	Bearer Access Token	json { "razorpay_order_id":"order_Oi8s4wTAQtk4J0", "razorpay_payment_id":"pay_Oi8s6hBQsBqCa2", "razorpay_signature":"0a6c753e3d8fc1a1b34281a51981468e3d1d4de9c195485e0fb0c5154e4d3e6f" }	json { "message":"Payment verified successfully" }	Validation/Auth errors
22	Razorpay Webhook	POST	http://localhost:8000/api/v1/payments/webhook	Razorpay Webhook Signature	json { "event":"payment.captured", "payload":{ "payment":{ "entity":{ "id":"pay_Oi8s6hBQsBqCa2", "order_id":"order_Oi8s4wTAQtk4J0", "amount":1100, "currency":"INR", "status":"captured" } } } }	json { "status":"ok" }	Invalid webhook signature
23	Admin - Refund Payment	POST	http://localhost:8000/api/v1/payments/admin/{id}/refund	Bearer Admin Access Token	Path Parameter: id (Payment ID)	json { "message":"Refund processed successfully", "refund_id":"rfnd_OiSG7B2G7sxIQa" }	401 / 403 / 404
24	Create Enquiry	POST	http://localhost:8000/api/v1/enquiries/	No	json { "name":"Rahul", "email":"rahul@example.com", "phone":"+911234567890", "subject":"Puja Booking", "message":"I would like to book a Lakshmi Puja for Navratri" }	json { "id":1, "name":"Rahul", "email":"rahul@example.com", "phone":"+911234567890", "subject":"Puja Booking", "message":"I would like to book a Lakshmi Puja for Navratri", "status":"OPEN", "admin_reply":null, "created_at":"2024-09-20T10:00:00Z", "updated_at":null }	Validation errors
25	Admin - List Enquiries	GET	http://localhost:8000/api/v1/enquiries/admin?status=OPEN	Bearer Admin Access Token	Query Parameter: status=OPEN	json [ { "id":1, "...":"Enquiry Object", "status":"OPEN" } ]	401 / 403
26	Admin - Respond to Enquiry	PATCH	http://localhost:8000/api/v1/enquiries/admin/{id}/respond	Bearer Admin Access Token	json { "admin_reply":"Thank you for your enquiry. We will get back to you shortly." }	Full enquiry object with status changed to RESOLVED and admin_reply populated	Validation/Auth errors
27	Admin - Update Enquiry Status	PATCH	http://localhost:8000/api/v1/enquiries/admin/{id}/status	Bearer Admin Access Token	json { "status":"IN_PROGRESS" }	Updated enquiry object	Validation/Auth errors
28	Admin Login	POST	http://localhost:8000/api/v1/admin/auth/login	No	json { "email":"admin@mahalaxmipuja.com", "password":"admin123" }	json { "message":"2FA OTP sent", "admin_id":1 }	429 json { "detail":"Too many failed login attempts. Account locked for 15 minutes." }
							
29	Admin Verify 2FA	POST	http://localhost:8000/api/v1/admin/auth/verify-2fa	No	json { "admin_id":1, "otp":"483920" }	json { "access_token":"eyJhbGciOiJIUzI1NiIs...", "refresh_token":"eyJhbGciOiJIUzI1NiIs...", "token_type":"bearer" }	Invalid OTP / Validation errors
30	Admin Dashboard Summary	GET	http://localhost:8000/api/v1/admin/dashboard/summary	Bearer Admin Access Token	None	json { "total_users":42, "total_orders":15, "total_revenue":16500, "today_bookings":3, "today_revenue":3300 }	401 / 403
31	Admin - Recent Orders	GET	http://localhost:8000/api/v1/admin/dashboard/recent-orders	Bearer Admin Access Token	None	Array containing the 10 most recent order objects. Example: json [ { "id":1, "order_id":"MLX-20240115-AB12", "status":"PENDING", "...":"Order Object" } ]	401 / 403
32	Admin - Recent Payments	GET	http://localhost:8000/api/v1/admin/dashboard/recent-payments	Bearer Admin Access Token	None	Array containing the 10 most recent payment objects. Example: json [ { "id":1, "order_id":1, "razorpay_order_id":"order_Oi8s4wTAQtk4J0", "status":"PENDING", "...":"Payment Object" } ]	401 / 403
33	Admin - List All Users	GET	http://localhost:8000/api/v1/admin/users/	Bearer Admin Access Token	None	json [ { "id":1, "first_name":"John", "last_name":"Doe", "email":"john@example.com", "phone_number":"+919876543210", "...":"User Object" } ]	401 / 403
34	Admin - Get User By ID	GET	http://localhost:8000/api/v1/admin/users/{id}	Bearer Admin Access Token	Path Parameter: id	Complete User Object	401 / 403 / 404
35	Create Admin User	POST	http://localhost:8000/api/v1/admin/users/	Bearer Admin Access Token	json { "phone_number":"+919999999999", "email":"newadmin@example.com", "password":"securepassword", "first_name":"New", "last_name":"Admin" }	Complete User JSON with "is_admin": true	Validation / 401 / 403
36	Update User Active Status	PATCH	http://localhost:8000/api/v1/admin/users/{id}/status	Bearer Admin Access Token	json { "is_active": false }	Updated User Object	Validation / 401 / 403 / 404
37	Root API	GET	http://localhost:8000/api/v1/	No	None	json { "message":"Welcome to MahalaxmiPuja.com API" }	None specified
38	Health Check	GET	http://localhost:8000/api/v1/health	No	None	json { "status":"healthy", "version":"1.0.0" }	None specified