import { useState, useEffect } from 'react';
import { attendanceAPI, employeeAPI } from '../api';

interface Employee {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  department: string;
}

interface Attendance {
  id: number;
  employee_id: string;
  date: string;
  status: string;
}

function AttendanceManagement() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('');
  const [presentDays, setPresentDays] = useState<{ [key: string]: number }>({});

  const [formData, setFormData] = useState({
    employee_id: '',
    date: new Date().toISOString().split('T')[0],
    status: 'Present',
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([fetchEmployees(), fetchAttendance()]);
  }, []);

  useEffect(() => {
    if (selectedEmployeeId) {
      fetchEmployeePresentDays(selectedEmployeeId);
    }
  }, [selectedEmployeeId]);

  const fetchEmployees = async () => {
    try {
      const response = await employeeAPI.getEmployees();
      setEmployees(response.data);
    } catch (err: any) {
      console.error('Failed to fetch employees');
    }
  };

  const fetchAttendance = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await attendanceAPI.getAttendance();
      setAttendanceRecords(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch attendance records');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployeePresentDays = async (employeeId: string) => {
    try {
      const response = await attendanceAPI.getPresentDays(employeeId);
      setPresentDays(prev => ({
        ...prev,
        [employeeId]: response.data.present_days
      }));
    } catch (err: any) {
      console.error('Failed to fetch present days');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      await attendanceAPI.createAttendance(formData);
      setSuccess('Attendance marked successfully!');
      setFormData({
        employee_id: '',
        date: new Date().toISOString().split('T')[0],
        status: 'Present',
      });
      setShowForm(false);
      await fetchAttendance();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to mark attendance';
      setError(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  const getEmployeeName = (employeeId: string) => {
    const employee = employees.find(e => e.employee_id === employeeId);
    return employee ? employee.full_name : employeeId;
  };

  const filteredRecords = selectedEmployeeId
    ? attendanceRecords.filter(r => r.employee_id === selectedEmployeeId)
    : attendanceRecords;

  const sortedRecords = [...filteredRecords].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <div className="section">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 className="section-title">Attendance Management</h2>
        <button 
          className="button button-primary"
          onClick={() => setShowForm(!showForm)}
          disabled={employees.length === 0}
          title={employees.length === 0 ? 'Please add employees first' : ''}
        >
          {showForm ? '✕ Cancel' : '➕ Mark Attendance'}
        </button>
      </div>

      {employees.length === 0 && (
        <div className="alert alert-warning">
          ⚠️ No employees found. Please add employees first before marking attendance.
        </div>
      )}

      {error && <div className="alert alert-error">⚠️ {error}</div>}
      {success && <div className="alert alert-success">✓ {success}</div>}

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', padding: '1.5rem', backgroundColor: '#f9fafb', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.125rem', fontWeight: '600' }}>Mark Attendance</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="employee_id">Employee *</label>
              <select
                id="employee_id"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Employee</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.employee_id}>
                    {emp.employee_id} - {emp.full_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="date">Date *</label>
              <input
                id="date"
                type="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="status">Status *</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                required
              >
                <option value="Present">Present</option>
                <option value="Absent">Absent</option>
              </select>
            </div>
          </div>

          <div className="button-group">
            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? 'Marking...' : 'Mark Attendance'}
            </button>
            <button 
              type="button" 
              className="button button-secondary"
              onClick={() => setShowForm(false)}
              disabled={submitting}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.125rem', fontWeight: '600' }}>Filter by Employee</h3>
        <select
          value={selectedEmployeeId}
          onChange={(e) => setSelectedEmployeeId(e.target.value)}
          style={{ width: '100%', maxWidth: '400px', padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: '6px' }}
        >
          <option value="">All Employees</option>
          {employees.map(emp => (
            <option key={emp.id} value={emp.employee_id}>
              {emp.employee_id} - {emp.full_name} ({presentDays[emp.employee_id] || 0} days present)
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : sortedRecords.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <h3>{selectedEmployeeId ? 'No Attendance Records' : 'No Attendance Records'}</h3>
          <p>{selectedEmployeeId ? 'No attendance records found for this employee.' : 'Start by marking attendance for your employees.'}</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Employee ID</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {sortedRecords.map(record => (
                <tr key={record.id}>
                  <td>{getEmployeeName(record.employee_id)}</td>
                  <td><strong>{record.employee_id}</strong></td>
                  <td>{new Date(record.date).toLocaleDateString()}</td>
                  <td>
                    <span className={`badge ${record.status === 'Present' ? 'badge-success' : 'badge-danger'}`}>
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AttendanceManagement;
