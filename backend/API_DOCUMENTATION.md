
# Multi-Tenant SaaS Customer Service API Documentation

## Overview

This is a multi-tenant SaaS customer service application that identifies tenants via HTTP Host header and integrates with external AI APIs for chat functionality.

## Tenant Identification

The system identifies tenants based on the HTTP Host header in requests. Each tenant should have a unique domain (e.g., `tenant1.myapp.com`, `tenant2.myapp.com`).

For development, the system accepts `localhost` and automatically maps it to the first available tenant.

## API Endpoints

### 1. Chat API Call
**Endpoint:** `POST /api/chat/call/`

Makes a chat request to the external AI API using tenant-specific configuration.

**Request Body:**
```json
{
    "prompt": "Explain the theory of relativity simply",
    "model": "gpt-3.5-turbo",  // Optional, defaults to gpt-3.5-turbo
    "seed": "12345",           // Optional
    "customer_id": "uuid"      // Optional, links chat to specific customer
}
```

**Response:**
```json
{
    "success": true,
    "message_id": "uuid",
    "prompt": "Explain the theory of relativity simply",
    "response": "AI response text...",
    "model": "gpt-3.5-turbo",
    "response_time_ms": 1500,
    "tokens_remaining": 999,
    "tenant": "Demo Company"
}
```

### 2. Chat History
**Endpoint:** `GET /api/chat/history/`

Retrieves chat history for the current tenant.

**Query Parameters:**
- `limit`: Number of messages to return (max 100, default 50)
- `offset`: Offset for pagination (default 0)

**Response:**
```json
{
    "success": true,
    "messages": [
        {
            "id": "uuid",
            "prompt": "User prompt",
            "response": "AI response",
            "created_at": "2024-01-15T10:30:00Z",
            "model": "gpt-3.5-turbo",
            "tokens_used": 1,
            "response_time_ms": 1500
        }
    ],
    "total_messages": 25,
    "tenant": "Demo Company",
    "tokens_used": 25,
    "tokens_limit": 1000
}
```

### 3. Add Customer Data
**Endpoint:** `POST /api/customer/add/`

Adds customer data for the current tenant.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",    // Optional
    "phone": "+1234567890",         // Optional
    "data": {                       // Optional additional data
        "company": "Acme Corp",
        "preferences": ["email", "sms"]
    }
}
```

**Response:**
```json
{
    "success": true,
    "customer_id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Tenant Information
**Endpoint:** `GET /api/tenant/info/`

Gets information about the current tenant.

**Response:**
```json
{
    "success": true,
    "tenant": {
        "id": "uuid",
        "name": "Demo Company",
        "domain": "localhost",
        "tokens_used": 25,
        "tokens_limit": 1000,
        "tokens_remaining": 975,
        "system_parameter": "You are a helpful customer service assistant...",
        "created_at": "2024-01-15T09:00:00Z"
    }
}
```

## Error Responses

All endpoints may return these error responses:

**Tenant Not Found (404):**
```json
{
    "error": "Tenant not found or inactive",
    "message": "Please check your domain configuration"
}
```

**Token Limit Exceeded (429):**
```json
{
    "error": "Token limit exceeded",
    "message": "Tenant has used 1000/1000 tokens"
}
```

**Invalid Request (400):**
```json
{
    "error": "Missing prompt",
    "message": "Please provide a prompt in the request body"
}
```

## Usage Examples

### Using curl

```bash
# Chat API call
curl -X POST http://localhost:3000/api/chat/call/ \
  -H "Content-Type: application/json" \
  -H "Host: tenant1.myapp.com" \
  -d '{"prompt": "Hello, how can you help me today?"}'

# Get chat history
curl -X GET http://localhost:3000/api/chat/history/?limit=10 \
  -H "Host: tenant1.myapp.com"

# Add customer
curl -X POST http://localhost:3000/api/customer/add/ \
  -H "Content-Type: application/json" \
  -H "Host: tenant1.myapp.com" \
  -d '{"name": "Jane Smith", "email": "jane@example.com"}'
```

### Using JavaScript/Fetch

```javascript
// Chat API call
fetch('/api/chat/call/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        prompt: 'What are your business hours?',
        model: 'gpt-3.5-turbo'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Development Setup

1. Create and activate virtual environment (if not using Replit)
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create sample tenant: `python manage.py create_sample_tenant`
5. Create superuser: `python manage.py createsuperuser`
6. Start server: `python manage.py runserver 0.0.0.0:3000`

## Admin Interface

Access the Django admin interface at `/admin/` to manage tenants, customer data, and chat messages.

The admin interface allows you to:
- Create and manage tenants
- Set tenant-specific system parameters
- Monitor token usage
- View chat history
- Manage customer data

## Multi-Tenant Architecture

- **Shared Database, Shared Schema**: All tenants use the same database tables
- **Data Isolation**: Each record has a `tenant` foreign key for isolation
- **Host-based Identification**: Tenants identified by HTTP Host header
- **Token Limits**: Each tenant has configurable API token limits
- **Custom System Parameters**: Each tenant can have custom AI behavior
