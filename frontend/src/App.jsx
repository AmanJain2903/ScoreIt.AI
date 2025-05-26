import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import VerifyEmail from './pages/VerifyEmail';
import ProtectedRoute from './ProtectedRoute'; // or inline if not separating

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/auth" element={<Auth />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/auth" />} />
        <Route path="/verify" element={<VerifyEmail />} />
      </Routes>
    </Router>
  );
}

export default App;