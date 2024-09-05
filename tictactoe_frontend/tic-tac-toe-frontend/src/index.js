import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Playboard from './playboard'; // 引入Playboard组件
import reportWebVitals from './reportWebVitals';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // 引入react-router-dom中的组件

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/playboard" element={<Playboard />} />
      </Routes>
    </Router>
  </React.StrictMode>
);