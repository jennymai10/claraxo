import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Login from './login';
import Playboard from './playboard';
import Signup from './signup';
import Settings from './settings';
import VerifyEmail from './verify_email';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/new_game" element={<Playboard />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verifyemail" element={<VerifyEmail />} />
        <Route path="/verifyemail/:username" element={<VerifyEmail />} />
        <Route path="/history" element={<VerifyEmail />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Router>
  </React.StrictMode>
);