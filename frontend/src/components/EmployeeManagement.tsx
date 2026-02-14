import { useState, useEffect } from 'react';
import { employeeAPI } from '../api';

interface Employee {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  department: string;
}

function EmployeeManagement() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    employee_id: '',
    full_name: '',
    email: '',
    department: '',
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await employeeAPI.getEmployees();
      setEmployees(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch employees');
    } finally {
      setLoading(false);
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
      await employeeAPI.createEmployee(formData);
      setSuccess('Employee added successfully!');
      setFormData({ employee_id: '', full_name: '', email: '', department: '' });
      setShowForm(false);
      await fetchEmployees();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 
                      (Array.isArray(err.response?.data?.detail) 
                        ? err.response.data.detail[0]?.msg 
                        : 'Failed to add employee');
      setError(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (employeeId: string) => {
    if (!window.confirm(`Are you sure you want to delete employee ${employeeId}?`)) {
      return;
    }

    setError('');
    setSuccess('');

    try {
      await employeeAPI.deleteEmployee(employeeId);
      setSuccess('Employee deleted successfully!');
      await fetchEmployees();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete employee');
    }
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2 className="section-title">👥 Employee Management</h2>
        <button 
          className="button button-primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? '✕ Cancel' : '➕ Add Employee'}
        </button>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}
      {success && <div className="alert alert-success">✓ {success}</div>}

      {showForm && (
        <form onSubmit={handleSubmit} className="form-container">
          <h3>Add New Employee</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="employee_id">Employee ID *</label>
              <input
                id="employee_id"
                type="text"
                name="employee_id"
                value={formData.employee_id}
                onChange={handleInputChange}
                required
                placeholder="e.g., EMP001"
              />
            </div>

            <div className="form-group">
              <label htmlFor="full_name">Full Name *</label>
              <input
                id="full_name"
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                required
                placeholder="e.g., John Doe"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="e.g., john@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="department">Department *</label>
              <select
                id="department"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Department</option>
                <option value="HR">HR</option>
                <option value="IT">IT</option>
                <option value="Finance">Finance</option>
                <option value="Marketing">Marketing</option>
                <option value="Operations">Operations</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="button-group">
            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add Employee'}
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

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : employees.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👥</div>
          <h3>No Employees Found</h3>
          <p>Start by adding your first employee to the system.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td><strong>{employee.employee_id}</strong></td>
                  <td>{employee.full_name}</td>
                  <td>{employee.email}</td>
                  <td>{employee.department}</td>
                  <td>
                    <div className="actions">
                      <button
                        className="button button-danger button-small"
                        onClick={() => handleDelete(employee.employee_id)}
                      >
                        Delete
                      </button>
                    </div>
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

export default EmployeeManagement;
