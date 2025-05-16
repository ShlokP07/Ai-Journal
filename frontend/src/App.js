// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import JournalPage from './JournalPage';
import ProfileSetup from './ProfileSetup';
import AuthPage from './AuthPage';

export default function App() {
  return (
    <Router>
      <div className="p-4 max-w-4xl mx-auto">
        <nav className="mb-6 flex gap-4">
          <Link to="/" className="text-blue-600 hover:underline">Journal</Link>
          <Link to="/setup" className="text-blue-600 hover:underline">Set Up Profile</Link>
          <Link to="/auth" className="text-blue-600 hover:underline">Login/Register</Link>
        </nav>
        <Routes>
          <Route path="/" element={<JournalPage />} />
          <Route path="/setup" element={<ProfileSetup />} />
          <Route path="/auth" element={<AuthPage />} />
        </Routes>
      </div>
    </Router>
  );
}
