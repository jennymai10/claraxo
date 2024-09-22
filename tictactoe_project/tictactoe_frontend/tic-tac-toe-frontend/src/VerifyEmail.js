import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { useNavigate, useParams } from 'react-router-dom';

function get_cookie(name) {
    let cookie_value = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookie_value;
}

function VerifyEmail() {
    const params = useParams();
    const [username, set_username] = useState(params.username || '');
    const [verification_code, set_verification_code] = useState('');
    const [error, set_error] = useState({});
    const navigate = useNavigate();

    // Handle input changes and validate in real-time
    const handle_change = (setter, validate_fn) => (event) => {
        setter(event.target.value);
        if (validate_fn) validate_fn(event.target.value);
    };

    // Validate the verification code format (6 digits only)
    const is_valid_verification_code = (value) => {
        const code_pattern = /^\d{6}$/;
        if (!code_pattern.test(value)) {
            set_error(prev => ({ ...prev, verification_code: 'Invalid Verification Code. Must be 6 digits.' }));
            return false;
        }
        set_error(prev => ({ ...prev, verification_code: '' }));
        return true;
    };

    const handle_verify_click = async (event) => {
        event.preventDefault();
        set_error({}); // Reset errors before validation

        if (is_valid_verification_code(verification_code)) {
            try {
                const form_data = new URLSearchParams();
                form_data.append('username', username);
                form_data.append('verification_code', verification_code);

                const response = await fetch('http://localhost:8000/verifyemail/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': get_cookie('csrftoken'),
                    },
                    credentials: 'include',
                    body: form_data.toString(),
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.status === 'success') {
                        navigate(data.redirect_url);
                    }
                } else {
                    console.log(data.errors);
                    if (data.errors) {
                        set_error(data.errors);
                    } else {
                        set_error({ submit: data.message });
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                set_error(prev => ({ ...prev, submit: 'An error occurred during verification. Please try again.' }));
            }
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <img src={board} className="App-board" draggable="false" />
                <img src={ruler} className="App-ruler" draggable="false" />
                <img src={pencil} className="App-pencil" draggable="false" />

                <div className="App-container">
                    <div className="App-SignupForm">
                        <div className="App-FormName">
                            <h4>verify email</h4>
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
                                        onChange={(e) => set_username(e.target.value)} 
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
                                        onChange={handle_change(set_verification_code, is_valid_verification_code)}
                                    />
                                </div>
                                {error.verification_code && <p className='Form-Error'>{error.verification_code}</p>}
                            </div>
                            {error.submit && <p className='Form-Error'>{error.submit}</p>}
                            <div className="App-Panel">
                                <button className="App-Button" onClick={handle_verify_click}>
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