from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Date, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import date, datetime
from typing import List, Optional
import os
import re

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hrms.db")
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI(
    title="HRMS Lite API", 
    version="2.0.0",
    description="A production-ready Human Resource Management System"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class EmployeeDB(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AttendanceDB(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # "Present" or "Absent"
    remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    
    @field_validator('employee_id')
    @classmethod
    def validate_employee_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Employee ID cannot be empty')
        if len(v) > 50:
            raise ValueError('Employee ID cannot exceed 50 characters')
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Employee ID can only contain alphanumeric characters, hyphens, and underscores')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Full Name cannot be empty')
        if len(v) < 2:
            raise ValueError('Full Name must be at least 2 characters long')
        if len(v) > 100:
            raise ValueError('Full Name cannot exceed 100 characters')
        if not re.match(r'^[a-zA-Z\s\-\']+$', v):
            raise ValueError('Full Name can only contain letters, spaces, hyphens, and apostrophes')
        return v
    
    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Department cannot be empty')
        if len(v) > 50:
            raise ValueError('Department cannot exceed 50 characters')
        return v

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Full Name cannot be empty')
            if len(v) < 2:
                raise ValueError('Full Name must be at least 2 characters long')
            if len(v) > 100:
                raise ValueError('Full Name cannot exceed 100 characters')
        return v
    
    @field_validator('department')
    @classmethod
    def validate_department(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Department cannot be empty')
            if len(v) > 50:
                raise ValueError('Department cannot exceed 50 characters')
        return v

class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: str  # "Present" or "Absent"
    remarks: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ["Present", "Absent"]:
            raise ValueError('Status must be "Present" or "Absent"')
        return v
    
    @field_validator('remarks')
    @classmethod
    def validate_remarks(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Remarks cannot exceed 500 characters')
        return v

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    remarks: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ["Present", "Absent"]:
            raise ValueError('Status must be "Present" or "Absent"')
        return v

class AttendanceResponse(BaseModel):
    id: int
    employee_id: str
    date: date
    status: str
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    detail: str
    status_code: int

class StatsResponse(BaseModel):
    total_employees: int
    total_attendance_records: int
    present_count: int
    absent_count: int

# Routes

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "2.0.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HRMS Lite API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }

# Statistics Route
@app.get("/api/statistics", response_model=StatsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    try:
        total_employees = db.query(func.count(EmployeeDB.id)).scalar() or 0
        total_attendance_records = db.query(func.count(AttendanceDB.id)).scalar() or 0
        present_count = db.query(func.count(AttendanceDB.id)).filter(AttendanceDB.status == "Present").scalar() or 0
        absent_count = db.query(func.count(AttendanceDB.id)).filter(AttendanceDB.status == "Absent").scalar() or 0
        
        return {
            "total_employees": total_employees,
            "total_attendance_records": total_attendance_records,
            "present_count": present_count,
            "absent_count": absent_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

# Dashboard Routes
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        from datetime import date as date_type
        today = date_type.today()
        
        total_employees = db.query(func.count(EmployeeDB.id)).scalar() or 0
        
        # Get unique departments
        departments = db.query(EmployeeDB.department).distinct().count()
        
        # Get today's attendance
        today_present = db.query(func.count(AttendanceDB.id)).filter(
            AttendanceDB.date == today,
            AttendanceDB.status == "Present"
        ).scalar() or 0
        
        today_absent = db.query(func.count(AttendanceDB.id)).filter(
            AttendanceDB.date == today,
            AttendanceDB.status == "Absent"
        ).scalar() or 0
        
        return {
            "total_employees": total_employees,
            "departments": departments,
            "present_today": today_present,
            "absent_today": today_absent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

# Employee Routes
@app.post("/api/employees", response_model=EmployeeResponse, status_code=201)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    try:
        # Check if employee_id already exists
        existing_emp_id = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee.employee_id.strip()).first()
        if existing_emp_id:
            raise HTTPException(status_code=409, detail="Employee ID already exists")
        
        # Check if email already exists
        existing_email = db.query(EmployeeDB).filter(EmployeeDB.email == employee.email.lower()).first()
        if existing_email:
            raise HTTPException(status_code=409, detail="Email already exists")
        
        db_employee = EmployeeDB(
            employee_id=employee.employee_id.strip(),
            full_name=employee.full_name.strip(),
            email=employee.email.lower(),
            department=employee.department.strip()
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating employee: {str(e)}")

@app.get("/api/employees", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all employees with optional filtering and pagination"""
    try:
        query = db.query(EmployeeDB)
        
        # Search filter
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (EmployeeDB.full_name.ilike(search_term)) |
                (EmployeeDB.employee_id.ilike(search_term)) |
                (EmployeeDB.email.ilike(search_term))
            )
        
        # Department filter
        if department:
            query = query.filter(EmployeeDB.department.ilike(f"%{department}%"))
        
        # Pagination
        employees = query.offset(skip).limit(limit).all()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employees: {str(e)}")

@app.get("/api/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, db: Session = Depends(get_db)):
    """Get a specific employee by ID"""
    try:
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id.strip()).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee: {str(e)}")

@app.put("/api/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: str, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee"""
    try:
        db_employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id.strip()).first()
        if not db_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check email uniqueness if being updated
        if employee.email and employee.email.lower() != db_employee.email:
            existing_email = db.query(EmployeeDB).filter(EmployeeDB.email == employee.email.lower()).first()
            if existing_email:
                raise HTTPException(status_code=409, detail="Email already exists")
            db_employee.email = employee.email.lower()
        
        if employee.full_name is not None:
            db_employee.full_name = employee.full_name.strip()
        if employee.department is not None:
            db_employee.department = employee.department.strip()
        
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating employee: {str(e)}")

@app.delete("/api/employees/{employee_id}", status_code=204)
async def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """Delete an employee and associated attendance records"""
    try:
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id.strip()).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Delete attendance records for this employee
        db.query(AttendanceDB).filter(AttendanceDB.employee_id == employee_id.strip()).delete()
        db.delete(employee)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting employee: {str(e)}")

# Attendance Routes
@app.post("/api/attendance", response_model=AttendanceResponse, status_code=201)
async def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Create attendance record"""
    try:
        # Check if employee exists
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == attendance.employee_id.strip()).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if attendance for this date already exists
        existing = db.query(AttendanceDB).filter(
            AttendanceDB.employee_id == attendance.employee_id.strip(),
            AttendanceDB.date == attendance.date
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Attendance record for this date already exists")
        
        # Prevent future dates
        if attendance.date > date.today():
            raise HTTPException(status_code=400, detail="Cannot mark attendance for future dates")
        
        db_attendance = AttendanceDB(
            employee_id=attendance.employee_id.strip(),
            date=attendance.date,
            status=attendance.status,
            remarks=attendance.remarks
        )
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return db_attendance
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating attendance: {str(e)}")

@app.get("/api/attendance", response_model=List[AttendanceResponse])
async def get_all_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all attendance records with filtering"""
    try:
        query = db.query(AttendanceDB)
        
        if employee_id:
            query = query.filter(AttendanceDB.employee_id == employee_id.strip())
        
        if status:
            if status not in ["Present", "Absent"]:
                raise HTTPException(status_code=400, detail="Invalid status")
            query = query.filter(AttendanceDB.status == status)
        
        if start_date:
            query = query.filter(AttendanceDB.date >= start_date)
        
        if end_date:
            query = query.filter(AttendanceDB.date <= end_date)
        
        attendance = query.order_by(AttendanceDB.date.desc()).offset(skip).limit(limit).all()
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@app.get("/api/attendance/{employee_id}", response_model=List[AttendanceResponse])
async def get_employee_attendance(
    employee_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get attendance records for specific employee"""
    try:
        # Check if employee exists
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id.strip()).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        attendance = db.query(AttendanceDB).filter(
            AttendanceDB.employee_id == employee_id.strip()
        ).order_by(AttendanceDB.date.desc()).offset(skip).limit(limit).all()
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@app.get("/api/attendance/{employee_id}/stats")
async def get_employee_attendance_stats(employee_id: str, db: Session = Depends(get_db)):
    """Get attendance statistics for an employee"""
    try:
        # Check if employee exists
        employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id.strip()).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        total = db.query(func.count(AttendanceDB.id)).filter(
            AttendanceDB.employee_id == employee_id.strip()
        ).scalar() or 0
        
        present = db.query(func.count(AttendanceDB.id)).filter(
            AttendanceDB.employee_id == employee_id.strip(),
            AttendanceDB.status == "Present"
        ).scalar() or 0
        
        absent = db.query(func.count(AttendanceDB.id)).filter(
            AttendanceDB.employee_id == employee_id.strip(),
            AttendanceDB.status == "Absent"
        ).scalar() or 0
        
        return {
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "total_records": total,
            "present_days": present,
            "absent_days": absent,
            "attendance_percentage": round((present / total * 100) if total > 0 else 0, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.put("/api/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(attendance_id: int, attendance: AttendanceUpdate, db: Session = Depends(get_db)):
    """Update attendance record"""
    try:
        db_attendance = db.query(AttendanceDB).filter(AttendanceDB.id == attendance_id).first()
        if not db_attendance:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        if attendance.status is not None:
            db_attendance.status = attendance.status
        if attendance.remarks is not None:
            db_attendance.remarks = attendance.remarks
        
        db.commit()
        db.refresh(db_attendance)
        return db_attendance
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating attendance: {str(e)}")

@app.delete("/api/attendance/{attendance_id}", status_code=204)
async def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Delete attendance record"""
    try:
        record = db.query(AttendanceDB).filter(AttendanceDB.id == attendance_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        db.delete(record)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting attendance: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
