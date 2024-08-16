import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './Login';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/" element={<Navigate to="/login" />} />
                    {/* Other routes */}
                </Routes>
            </div>
        </Router>
    );
}

export default App;
