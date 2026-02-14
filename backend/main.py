from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
from typing import List
import os

# Database setup
DATABASE_URL = "sqlite:///./hrms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI(title="HRMS Lite API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class EmployeeDB(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)

class AttendanceDB(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)
    date = Column(Date)
    status = Column(String)  # "Present" or "Absent"

Base.metadata.create_all(bind=engine)

# Pydantic Models
class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str
    
    @field_validator('employee_id')
    @classmethod
    def employee_id_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Employee ID cannot be empty')
        return v
    
    @field_validator('full_name')
    @classmethod
    def full_name_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Full Name cannot be empty')
        return v
    
    @field_validator('department')
    @classmethod
    def department_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Department cannot be empty')
        return v

class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    full_name: str
    email: str
    department: str
    
    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    employee_id: str
    date: date
    status: str  # "Present" or "Absent"
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ["Present", "Absent"]:
            raise ValueError('Status must be "Present" or "Absent"')
        return v

class AttendanceResponse(BaseModel):
    id: int
    employee_id: str
    date: date
    status: str
    
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
async def root():
    return {"message": "HRMS Lite API is running"}

# Employee Routes
@app.post("/api/employees", response_model=EmployeeResponse, status_code=201)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    # Check if employee_id already exists
    existing_emp_id = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee.employee_id).first()
    if existing_emp_id:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Check if email already exists
    existing_email = db.query(EmployeeDB).filter(EmployeeDB.email == employee.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_employee = EmployeeDB(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.get("/api/employees", response_model=List[EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)):
    employees = db.query(EmployeeDB).all()
    return employees

@app.get("/api/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.delete("/api/employees/{employee_id}", status_code=204)
async def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Delete attendance records for this employee
    db.query(AttendanceDB).filter(AttendanceDB.employee_id == employee_id).delete()
    db.delete(employee)
    db.commit()
    return None

# Attendance Routes
@app.post("/api/attendance", response_model=AttendanceResponse, status_code=201)
async def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    # Check if employee exists
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == attendance.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if attendance for this date already exists
    existing = db.query(AttendanceDB).filter(
        AttendanceDB.employee_id == attendance.employee_id,
        AttendanceDB.date == attendance.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance record for this date already exists")
    
    db_attendance = AttendanceDB(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@app.get("/api/attendance", response_model=List[AttendanceResponse])
async def get_all_attendance(db: Session = Depends(get_db)):
    attendance = db.query(AttendanceDB).all()
    return attendance

@app.get("/api/attendance/{employee_id}", response_model=List[AttendanceResponse])
async def get_employee_attendance(employee_id: str, db: Session = Depends(get_db)):
    # Check if employee exists
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    attendance = db.query(AttendanceDB).filter(AttendanceDB.employee_id == employee_id).all()
    return attendance

@app.get("/api/attendance/{employee_id}/present-days")
async def get_present_days(employee_id: str, db: Session = Depends(get_db)):
    # Check if employee exists
    employee = db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    present_count = db.query(AttendanceDB).filter(
        AttendanceDB.employee_id == employee_id,
        AttendanceDB.status == "Present"
    ).count()
    
    return {"employee_id": employee_id, "present_days": present_count}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
