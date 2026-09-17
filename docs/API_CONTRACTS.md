# API Contracts

API contracts allow frontend and backend developers to work simultaneously.

> **TBD — DECIDE AFTER PROBLEM STATEMENT:** Actual APIs based on product needs.

## Template

- **Endpoint:** `/api/example`
- **HTTP Method:** `GET` | `POST` | `PUT` | `DELETE`
- **Authentication Requirement:** `None` | `Bearer Token`
- **Request Schema:**
  ```json
  {
    "example_field": "string"
  }
  ```
- **Response Schema:**
  ```json
  {
    "data": "string"
  }
  ```
- **Error Format:**
  ```json
  {
    "error": "Message"
  }
  ```
- **Status Codes:**
  - `200 OK`
  - `400 Bad Request`
  - `401 Unauthorized`
- **Owner:** Backend Developer (e.g., Ramraj)
- **Frontend Consumer:** Frontend Developer (e.g., Nikhil)
- **Backend Implementation Status:** `Not Started` | `In Progress` | `Done`

