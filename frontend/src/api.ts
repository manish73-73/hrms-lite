import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const employeeAPI = {
  createEmployee: (data: any) => apiClient.post('/api/employees', data),
  getEmployees: () => apiClient.get('/api/employees'),
  getEmployee: (employeeId: string) => apiClient.get(`/api/employees/${employeeId}`),
  deleteEmployee: (employeeId: string) => apiClient.delete(`/api/employees/${employeeId}`),
};

export const attendanceAPI = {
  createAttendance: (data: any) => apiClient.post('/api/attendance', data),
  getAttendance: () => apiClient.get('/api/attendance'),
  getEmployeeAttendance: (employeeId: string) => apiClient.get(`/api/attendance/${employeeId}`),
  getPresentDays: (employeeId: string) => apiClient.get(`/api/attendance/${employeeId}/present-days`),
};
