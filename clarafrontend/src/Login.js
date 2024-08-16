import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        axios.post('http://localhost:8000/auth/login/', {
            username: username,
            password: password
        })
        .then(response => {
            localStorage.setItem('token', response.data.key);
            navigate('/');
        })
        .catch(error => {
            console.error("There was an error logging in!", error);
        });
    };

    return (
        <div>
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Username:</label>
                    <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
                </div>
                <div>
                    <label>Password:</label>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    );
};

export default Login;

// // This code chunk is to verify that frontend is connected to backend or not.
// import React, { useEffect, useState } from 'react';
// import axios from 'axios';

// const Login = () => {
//     const [backendStatus, setBackendStatus] = useState('Checking...');

//     useEffect(() => {
//         axios.get('http://localhost:8000/api/status/')
//             .then(response => {
//                 setBackendStatus(response.data.status);
//             })
//             .catch(error => {
//                 console.error('Error connecting to the backend:', error);
//                 setBackendStatus('Backend is not reachable');
//             });
//     }, []);

//     return (
//         <div>
//             <h2>Login Page</h2>
//             <p>{backendStatus}</p>
//             {/* Your login form here */}
//         </div>
//     );
// };

// export default Login;
