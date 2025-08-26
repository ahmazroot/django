
# Multi-Tenant SaaS Chat Application

A modern multi-tenant SaaS customer service application with Django backend and React frontend.

## Architecture

```
myproject/
├── backend/        # Django API server
│   ├── apps/
│   │   ├── tenants/    # Tenant management
│   │   └── api/        # Chat API endpoints
│   ├── django_project/ # Django settings
│   └── manage.py
└── frontend/       # React chat interface
    ├── src/
    │   ├── App.tsx     # Main chat component
    │   └── App.css     # Styling
    └── package.json
```

## Features

- **Multi-tenant architecture** with shared database
- **Host-based tenant identification** (no authentication required)
- **Real-time chat interface** with AI integration
- **Token usage tracking** per tenant
- **Modern React UI** with TypeScript
- **RESTful API** endpoints

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py create_sample_tenant
python manage.py runserver 0.0.0.0:3000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The React app will run on http://localhost:3001 and proxy API requests to the Django backend on http://localhost:3000.

### Development Script

Use the provided script to start both servers:

```bash
chmod +x start-dev.sh
./start-dev.sh
```

## API Endpoints

- `POST /api/chat/call/` - Send chat message to AI
- `GET /api/chat/history/` - Get chat history
- `GET /api/tenant/info/` - Get tenant information
- `POST /api/customer/add/` - Add customer data

## Environment Variables

Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:3000
```

## Deployment

### Backend
Deploy Django backend as a web service on port 3000.

### Frontend
Build React app and deploy as static files:
```bash
cd frontend
npm run build
```

## Multi-Tenant Usage

Each tenant is identified by their domain:
- `tenant1.myapp.com` → Tenant 1
- `tenant2.myapp.com` → Tenant 2
- `localhost` → Default to first tenant (development)

## Technology Stack

- **Backend**: Django 5.0, SQLite, Django REST Framework
- **Frontend**: React 18, TypeScript, CSS3
- **AI Integration**: External API calls with configurable parameters
- **Database**: Shared schema with tenant isolation

## Development

The application uses:
- Django development server for backend API
- React development server with hot reload
- CORS enabled for cross-origin requests
- TypeScript for type safety

## Features

### Chat Interface
- Modern, responsive chat UI
- Real-time message display
- Typing indicators
- Message history
- Token usage tracking

### Multi-Tenant Support
- Host header identification
- Tenant-specific configurations
- Shared database with data isolation
- Token limit management

### API Integration
- External AI API integration
- Configurable model parameters
- Response time tracking
- Error handling
