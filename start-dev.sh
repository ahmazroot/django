
#!/bin/bash

echo "Starting Multi-Tenant Chat Application..."

# Start Django backend
echo "Starting Django backend on port 3000..."
cd backend && python manage.py runserver 0.0.0.0:3000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start React frontend
echo "Starting React frontend on port 3001..."
cd frontend && npm start &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend running on: http://localhost:3000"
echo "Frontend running on: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
