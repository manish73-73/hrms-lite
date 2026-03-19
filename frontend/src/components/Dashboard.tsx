import { useState, useEffect } from 'react';
import { employeeAPI, attendanceAPI } from '../api';
import '../styles/Dashboard.css';

interface Employee {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  department: string;
  created_at: string;
}

interface Attendance {
  id: number;
  employee_id: string;
  date: string;
  status: string;
}

interface AttendanceStats {
  employee_id: string;
  employee_name: string;
  total_records: number;
  present_days: number;
  absent_days: number;
  attendance_percentage: number;
}

function Dashboard() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [attendanceToday, setAttendanceToday] = useState<Attendance[]>([]);
  const [recentEmployees, setRecentEmployees] = useState<Employee[]>([]);
  const [allAttendance, setAllAttendance] = useState<Attendance[]>([]);
  const [attendanceStats, setAttendanceStats] = useState<AttendanceStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      const [empRes, attRes] = await Promise.all([
        employeeAPI.getEmployees(),
        attendanceAPI.getAttendance(),
      ]);

      const empData = empRes.data;
      const attData = attRes.data;

      setEmployees(empData);
      setAllAttendance(attData);

      // Get recently added employees (last 5)
      const recent = empData.slice().reverse().slice(0, 5);
      setRecentEmployees(recent);

      // Get today's attendance
      const today = new Date().toISOString().split('T')[0];
      const todayAtt = attData.filter((a: Attendance) => a.date === today);
      setAttendanceToday(todayAtt);

      // Get attendance stats for all employees
      const stats = await Promise.all(
        empData.map((emp: Employee) =>
          employeeAPI.getEmployeeStats(emp.employee_id)
            .then(res => res.data)
            .catch(() => null)
        )
      );
      setAttendanceStats(stats.filter(s => s !== null));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getDepartments = () => {
    const depts = new Set(employees.map(e => e.department));
    return depts.size;
  };

  const getPresentToday = () => {
    return attendanceToday.filter(a => a.status === 'Present').length;
  };

  const getAbsentToday = () => {
    return attendanceToday.filter(a => a.status === 'Absent').length;
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <button onClick={fetchDashboardData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Overview of your HR data</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card stat-card-primary">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Employees</p>
            <h3 className="stat-value">{employees.length}</h3>
          </div>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
          <div className="stat-content">
            <p className="stat-label">Departments</p>
            <h3 className="stat-value">{getDepartments()}</h3>
          </div>
        </div>

        <div className="stat-card stat-card-success">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <div className="stat-content">
            <p className="stat-label">Present Today</p>
            <h3 className="stat-value">{getPresentToday()}</h3>
          </div>
        </div>

        <div className="stat-card stat-card-danger">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
          </div>
          <div className="stat-content">
            <p className="stat-label">Absent Today</p>
            <h3 className="stat-value">{getAbsentToday()}</h3>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content-grid">
        {/* Recently Added Employees */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Recently Added</h2>
            <p className="card-subtitle">Last {recentEmployees.length} employees</p>
          </div>
          <div className="card-body">
            {recentEmployees.length === 0 ? (
              <div className="empty-state">
                <p>No employees added yet</p>
              </div>
            ) : (
              <div className="employees-list">
                {recentEmployees.map(emp => (
                  <div key={emp.id} className="employee-item">
                    <div className="employee-avatar">{getInitials(emp.full_name)}</div>
                    <div className="employee-info">
                      <p className="employee-name">{emp.full_name}</p>
                      <p className="employee-dept">{emp.department}</p>
                    </div>
                    <div className="employee-id">{emp.employee_id}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Today's Attendance */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Today's Attendance</h2>
            <p className="card-subtitle">{new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}</p>
          </div>
          <div className="card-body">
            {attendanceToday.length === 0 ? (
              <div className="empty-state">
                <p>No attendance marked today</p>
                <span className="empty-state-hint">No records have been marked yet for today</span>
              </div>
            ) : (
              <div className="attendance-list">
                {attendanceToday.map(att => {
                  const emp = employees.find(e => e.employee_id === att.employee_id);
                  return (
                    <div key={att.id} className={`attendance-item attendance-${att.status.toLowerCase()}`}>
                      <div className="attendance-marker"></div>
                      <div className="attendance-info">
                        <p className="attendance-employee">{emp?.full_name || att.employee_id}</p>
                        <p className="attendance-status">{att.status}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Overall Attendance Summary Table */}
      <div className="dashboard-card" style={{ marginTop: '2rem' }}>
        <div className="card-header">
          <h2>Overall Attendance Summary</h2>
          <p className="card-subtitle">All-time record per employee</p>
        </div>
        <div className="card-body">
          {attendanceStats.length === 0 ? (
            <div className="empty-state">
              <p>No attendance records yet</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>EMP ID</th>
                    <th>NAME</th>
                    <th>DEPARTMENT</th>
                    <th>PRESENT</th>
                    <th>ABSENT</th>
                    <th>RATE</th>
                  </tr>
                </thead>
                <tbody>
                  {attendanceStats.map(stat => {
                    const emp = employees.find(e => e.employee_id === stat.employee_id);
                    const rateColor = stat.attendance_percentage >= 80 ? 'good' : 
                                     stat.attendance_percentage >= 60 ? 'okay' : 'poor';
                    return (
                      <tr key={stat.employee_id}>
                        <td className="emp-id">{stat.employee_id}</td>
                        <td className="emp-name">{stat.employee_name}</td>
                        <td className="emp-dept">{emp?.department || '-'}</td>
                        <td className="present">{stat.present_days}</td>
                        <td className="absent">{stat.absent_days}</td>
                        <td className={`attendance-rate rate-${rateColor}`}>
                          <span className="rate-badge">{stat.attendance_percentage.toFixed(1)}%</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
