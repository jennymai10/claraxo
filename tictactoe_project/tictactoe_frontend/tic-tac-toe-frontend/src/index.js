import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import Login from './Login';
import Playboard from './playboard';
import Signup from './Signup';
import VerifyEmail from './VerifyEmail';
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
        <Route path="/verify_email" element={<VerifyEmail />} />
        <Route path="/verify_email/:username" element={<VerifyEmail />} />
      </Routes>
    </Router>
  </React.StrictMode>
);