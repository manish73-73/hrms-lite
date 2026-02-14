import './App.css';
import { useState } from 'react';
import EmployeeManagement from './components/EmployeeManagement';
import AttendanceManagement from './components/AttendanceManagement';

function App() {
  const [activeTab, setActiveTab] = useState<'employees' | 'attendance'>('employees');

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <h1>HRMS Lite</h1>
          <p>Human Resource Management System</p>
        </div>
      </header>

      <nav className="nav">
        <div className="container">
          <button
            className={`nav-button ${activeTab === 'employees' ? 'active' : ''}`}
            onClick={() => setActiveTab('employees')}
          >
            Employee Management
          </button>
          <button
            className={`nav-button ${activeTab === 'attendance' ? 'active' : ''}`}
            onClick={() => setActiveTab('attendance')}
          >
            Attendance Management
          </button>
        </div>
      </nav>

      <main className="container">
        {activeTab === 'employees' && <EmployeeManagement />}
        {activeTab === 'attendance' && <AttendanceManagement />}
      </main>

      <footer className="footer">
        <p>&copy; 2026 HRMS Lite. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
