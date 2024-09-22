import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { useNavigate } from 'react-router-dom';

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

function Signup() {
    const [username, set_username] = useState('');
    const [account_type, set_account_type] = useState('');
    const [email, set_email] = useState('');
    const [password, set_password] = useState('');
    const [password2, set_password2] = useState('');
    const [api_key, set_api_key] = useState('');
    const [age, set_age] = useState('');
    const [fullname, set_fullname] = useState('');
    const [error, set_error] = useState({});
    const [is_loading, set_is_loading] = useState(false);
    const navigate = useNavigate();

    const handle_change = (setter, validate_fn) => (event) => {
        setter(event.target.value);
        if (validate_fn) validate_fn(event.target.value);
    };

    const is_valid_username = (value) => {
        const username_pattern = /^[A-Za-z0-9_.-]{5,15}$/;
        if (!username_pattern.test(value)) {
            set_error(prev => ({ ...prev, username: 'Username must be 5-15 characters long and can only contain letters, numbers, (_), (-), and (.).' }));
            return false;
        } else if (value === '') {
            return true;
        }
        set_error(prev => ({ ...prev, username: '' }));
        return true;
    };

    const is_valid_email = (value) => {
        const email_pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email_pattern.test(value)) {
            set_error(prev => ({ ...prev, email: 'Please enter a valid email address.' }));
            return false;
        } else if (value === '') {
            return true;
        }
        set_error(prev => ({ ...prev, email: ''}));
        return true;
    };

    const is_valid_fullname = (value) => {
        const fullname_pattern = /^[A-Za-z\s]{2,30}$/;
        if (!fullname_pattern.test(value)) {
            set_error(prev => ({ ...prev, fullname: 'Full name can only have letters and spaces and must be between 2 and 30 characters.' }));
            return false;
        } else if (value === '') {
            return true;
        }
        set_error(prev => ({ ...prev, fullname: '' }));
        return true;
    };

    const is_valid_account_type = (value) => {
        if (value === "0") {
            set_error(prev => ({ ...prev, account_type: 'Account type is required.' }));
            return false;
        }
        set_error(prev => ({ ...prev, account_type: '' }));
        return true;
    };

    const is_valid_age = (value) => {
        const age_value = parseInt(value, 10);
        if (age_value < 0 || age_value > 120) {
            set_error(prev => ({ ...prev, age: 'Age must be a number between 0 and 120.' }));
            return false;
        } else if (age_value === '') {
            return true;
        }
        set_error(prev => ({ ...prev, age: '' }));
        return true;
    };

    const validate_passwords = (value) => {
        if (value !== password) {
            set_error(prev => ({ ...prev, password2: 'Passwords do not match.' }));
            return false;
        }
        set_error(prev => ({ ...prev, password2: '' }));
        return true;
    };

    const is_valid_password = (value) => {
        const password_pattern = /^(?=.*[A-Z])(?=.*\d).{7,25}$/;
        if (!password_pattern.test(value)) {
            set_error(prev => ({ ...prev, password: 'Password must be 7-25 characters long, with at least one uppercase letter and one number.' }));
            return false;
        } else if (value === '') {
            return true;
        }
        set_error(prev => ({ ...prev, password: '' }));
        return true;
    };

    const handle_signup_click = async (event) => {
        set_is_loading(true);
        event.preventDefault();
        set_error({});

        if (
            is_valid_username(username) &&
            is_valid_email(email) &&
            is_valid_fullname(fullname) &&
            is_valid_age(age) &&
            validate_passwords(password2) &&
            is_valid_password(password) &&
            is_valid_account_type(account_type)
        ) {
            try {
                const form_data = new URLSearchParams();
                form_data.append('account_type', account_type);
                form_data.append('email', email);
                form_data.append('password', password);
                form_data.append('password2', password2);
                form_data.append('age', age);
                form_data.append('username', username);
                form_data.append('api_key', api_key);
                form_data.append('profile_name', fullname);

                const response = await fetch('http://localhost:8000/register/', {
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
                set_error(prev => ({ ...prev, submit: 'An error occurred during signup. Please try again.' }));
            } finally {
                set_is_loading(false);
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
                            <h4>sign up</h4>
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
                                        onChange={handle_change(set_username, is_valid_username)}
                                    />
                                </div>
                                {error.username && <p className='Form-Error'>{error.username}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>account type</p>
                                </div>
                                <div className="App-Rectangle">
                                    <select
                                        className="Signup-AccountTypeSelect"
                                        value={account_type}
                                        onChange={handle_change(set_account_type, is_valid_account_type)}
                                    >
                                        <option value="0"></option>
                                        <option value="1">player</option>
                                        <option value="2">researcher</option>
                                    </select>
                                </div>
                                {error.account_type && <p className='Form-Error'>{error.account_type}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>email</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={email}
                                        placeholder=""
                                        onChange={handle_change(set_email, is_valid_email)}
                                    />
                                </div>
                                {error.email && <p className='Form-Error'>{error.email}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>password</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="password"
                                        value={password}
                                        placeholder=""
                                        onChange={handle_change(set_password, is_valid_password)}
                                    />
                                </div>
                                {error.password && <p className='Form-Error'>{error.password}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>re-enter password</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="password"
                                        value={password2}
                                        placeholder=""
                                        onChange={handle_change(set_password2, validate_passwords)}
                                    />
                                </div>
                                {error.password2 && <p className='Form-Error'>{error.password2}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>api key</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="password"
                                        value={api_key}
                                        placeholder=""
                                        onChange={handle_change(set_api_key)}
                                    />
                                </div>
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>age</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="number"
                                        value={age}
                                        placeholder=""
                                        onChange={handle_change(set_age, is_valid_age)}
                                    />
                                </div>
                                {error.age && <p className='Form-Error'>{error.age}</p>}
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>full name</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={fullname}
                                        placeholder=""
                                        onChange={handle_change(set_fullname, is_valid_fullname)}
                                    />
                                </div>
                                {error.fullname && <p className='Form-Error'>{error.fullname}</p>}
                            </div>
                            {error.submit && <p className='Form-Error'>{error.submit}</p>}
                            <div className="App-Panel">
                                <a href="/login">
                                    <div className="Signup-GoLoginText">
                                        <p>already have an account?</p>
                                    </div>
                                </a>
                                <button className="App-Button" onClick={handle_signup_click} disabled={is_loading}>
                                    {is_loading ? 'loading...' : 'sign up'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </header>
        </div>
    );
}

export default Signup;