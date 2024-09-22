import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { useNavigate, useParams } from 'react-router-dom';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function VerifyEmail() {
    const params = useParams();
    const [username, setUsername] = useState(params.username || '');
    const [verification_code, set_verification_code] = useState('');
    const [error, setError] = useState({});
    const navigate = useNavigate();

    // Handle input changes and validate in real-time
    const handleChange = (setter, validateFn) => (event) => {
        setter(event.target.value);
        if (validateFn) validateFn(event.target.value);
    };

    // Validate the verification code format (6 digits only)
    const is_valid_verification_code = (value) => {
        const code_pattern = /^\d{6}$/;
        if (!code_pattern.test(value)) {
            setError(prev => ({ ...prev, verification_code: 'Invalid Verification Code. Must be 6 digits.' }));
            return false;
        }
        setError(prev => ({ ...prev, verification_code: '' }));
        return true;
    };

    const handleVerifyClick = async (event) => {
        event.preventDefault();
        setError({}); // Reset errors before validation

        if (is_valid_verification_code(verification_code)) {
            try {
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('verification_code', verification_code);

                const response = await fetch('http://localhost:8000/verify_email/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    credentials: 'include',
                    body: formData.toString(),
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.status === 'success') {
                        navigate(data.redirect_url);
                    }
                } else {
                    console.log(data.errors);
                    if (data.errors) {
                        setError(data.errors);
                    } else {
                        setError({ submit: data.message });
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                setError(prev => ({ ...prev, submit: 'An error occurred during verification. Please try again.' }));
            }
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <img src={board} className="App-board" alt="board" />
                <img src={ruler} className="App-ruler" alt="ruler" />
                <img src={pencil} className="App-pencil" alt="pencil" />

                <div className="App-container">
                    <div className="App-SignupForm">
                        <div className="App-FormName">
                            <p>verify email</p>
                        </div>
                        <form>
                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>username</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={username}
                                        placeholder=""
                                        onChange={(e) => setUsername(e.target.value)} 
                                    />
                                </div>
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>verification code</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={verification_code}
                                        placeholder=""
                                        onChange={handleChange(set_verification_code, is_valid_verification_code)}
                                    />
                                </div>
                                {error.verification_code && <p className='Form-Error'>{error.verification_code}</p>}
                            </div>
                            {error.submit && <p className='Form-Error'>{error.submit}</p>}
                            <div className="App-Panel">
                                <button className="App-Button" onClick={handleVerifyClick}>
                                    verify
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </header>
        </div>
    );
}

export default VerifyEmail;