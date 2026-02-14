# Quick Start Guide - HRMS Lite

Get HRMS Lite up and running in minutes!

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hrms-lite.git
cd hrms-lite
```

### Step 2: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Backend will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Step 3: Start the Frontend (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Start Using

1. Open http://localhost:3000 in your browser
2. Go to "Employee Management" tab
3. Click "➕ Add Employee"
4. Fill in employee details and submit
5. Switch to "Attendance Management" to mark attendance

## 📋 Features Overview

### Employee Management
- ✅ Add new employees (Employee ID, Name, Email, Department)
- ✅ View all employees
- ✅ Delete employees
- ✅ Input validation (unique ID, valid email)

### Attendance Management
- ✅ Mark attendance (date, status: Present/Absent)
- ✅ View attendance records
- ✅ Filter by employee
- ✅ See total present days per employee

## 🛠️ Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Axios (HTTP client)
- CSS3 (responsive design)

### Backend
- FastAPI (Python framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- SQLite (database)

## 📚 API Endpoints

### Employees
- `POST /api/employees` - Create employee
- `GET /api/employees` - List all employees
- `GET /api/employees/{employee_id}` - Get specific employee
- `DELETE /api/employees/{employee_id}` - Delete employee

### Attendance
- `POST /api/attendance` - Mark attendance
- `GET /api/attendance` - Get all attendance records
- `GET /api/attendance/{employee_id}` - Get employee attendance
- `GET /api/attendance/{employee_id}/present-days` - Get present day count

## 🔍 Testing the API

### Using Swagger UI
1. Go to `http://localhost:8000/docs`
2. Try out endpoints interactively

### Using cURL

```bash
# Create employee
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": "IT"
  }'

# Get all employees
curl http://localhost:8000/api/employees

# Mark attendance
curl -X POST http://localhost:8000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "date": "2026-02-14",
    "status": "Present"
  }'
```

### Using Thunder Client / Postman
1. Import the API endpoints
2. Test with your employee IDs
3. Verify responses

## 📁 Project Structure

```
hrms-lite/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt      # Python dependencies
│   ├── Procfile             # Deployment config
│   └── venv/                # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main component
│   │   ├── api.ts           # API client
│   │   └── components/      # React components
│   ├── index.html           # HTML template
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite config
└── README.md                # Full documentation
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify virtual environment activated
# Install dependencies again
pip install -r requirements.txt -q
```

### Frontend won't load
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port if 3000 is busy
npm run dev -- --port 3001
```

### API connection error
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend API URL in .env.local
cat .env.local
```

## 📦 Building for Production

### Frontend Build
```bash
cd frontend
npm run build
# Output: dist/ directory ready for deployment
```

### Backend Deployment
See DEPLOYMENT.md for Railway/Render setup

## 🚢 Deployment

For full deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

Quick steps:
1. Push to GitHub
2. Deploy backend on Railway
3. Deploy frontend on Vercel
4. Set environment variables
5. Test live application

## 📞 Need Help?

- Check [README.md](README.md) for full documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- Review code comments in `main.py` and components
- Check browser console for client errors
- Check terminal for server errors

## ✅ Verification Checklist

After setup, verify:
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can add employee
- [ ] Can view employees
- [ ] Can mark attendance
- [ ] No errors in console/terminal
- [ ] Database file created (hrms.db)

## 🎉 You're All Set!

HRMS Lite is ready to use. Enjoy managing your HR data efficiently!

---

**Version:** 1.0  
**Last Updated:** February 2026
