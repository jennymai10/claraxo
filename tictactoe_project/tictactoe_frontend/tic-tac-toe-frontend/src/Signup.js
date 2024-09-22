import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { useNavigate } from 'react-router-dom';

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

function Signup() {
    const [username, setUsername] = useState('');
    const [accountType, setAccountType] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [api_key, setApiKey] = useState('');
    const [age, setAge] = useState('');
    const [fullname, setFullname] = useState('');
    const [error, setError] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    // Handle input changes and validate in real-time
    const handleChange = (setter, validateFn) => (event) => {
        setter(event.target.value);
        if (validateFn) validateFn(event.target.value);
    };

    // Validate username (5-15 characters, allows letters, numbers, '_', '-', and '.')
    const isValidUsername = (value) => {
        const usernamePattern = /^[A-Za-z0-9_.-]{5,15}$/;
        if (!usernamePattern.test(value)) {
            setError(prev => ({ ...prev, username: 'Username must be 5-15 characters long and can only contain letters, numbers, (_), (-), and (.).' }));
            return false;
        } else if (value === '') {
            return true
        }
        setError(prev => ({ ...prev, username: '' }));
        return true;
    };

    // Validate email format
    const isValidEmail = (value) => {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            setError(prev => ({ ...prev, email: 'Please enter a valid email address.' }));
            return false;
        } else if (value === '') {
            return true
        }
        setError(prev => ({ ...prev, email: ''}));
        return true;
    };

    // Validate profile name (only letters and spaces)
    const isValidFullName = (value) => {
        const profileNamePattern = /^[A-Za-z\s]{2,30}$/;
        if (!profileNamePattern.test(value)) {
            setError(prev => ({ ...prev, fullname: 'Full name can only has letters and spaces and must be between 2 and 30 characters.' }));
            return false;
        } else if (value === '') {
            return true
        }
        setError(prev => ({ ...prev, fullname: '' }));
        return true;
    };

    const isValidAccountType = (value) => {
        if (value === "0") {
            setError(prev => ({ ...prev, accountType: 'Account type is required.' }));
            return false;
        }
        setError(prev => ({ ...prev, accountType: '' }));
        return true;
    };

    // Validate age (between 0 and 120)
    const isValidAge = (value) => {
        const ageValue = parseInt(value, 10);
        if (ageValue < 0 || ageValue > 120) {
            setError(prev => ({ ...prev, age: 'Age must be a number between 0 and 120.' }));
            return false;
        } else if (ageValue === '') {
            return true
        }
        setError(prev => ({ ...prev, age: '' }));
        return true;
    };

    // Validate password match
    const validatePasswords = (value) => {
        if (value !== password) {
            setError(prev => ({ ...prev, password2: 'Passwords do not match.' }));
            return false;
        }
        setError(prev => ({ ...prev, password2: '' }));
        return true;
    };

    // Password strength check
    const isValidPassword = (value) => {
        const passwordPattern = /^(?=.*[A-Z])(?=.*\d).{7,25}$/;
        if (!passwordPattern.test(value)) {
            setError(prev => ({ ...prev, password: 'Password must be 7-25 characters long, with at least one uppercase letter and one number.' }));
            return false;
        } else if (value === '') {
            return true
        }
        setError(prev => ({ ...prev, password: '' }));
        return true;
    };

    const handleSignUpClick = async (event) => {
        setIsLoading(true);
        event.preventDefault();
        setError({}); // Reset errors before validation

        if (
            isValidUsername(username) &&
            isValidEmail(email) &&
            isValidFullName(fullname) &&
            isValidAge(age) &&
            validatePasswords(password2) &&
            isValidPassword(password) &&
            isValidAccountType(accountType)
        ) {
            try {
                const formData = new URLSearchParams();
                formData.append('account_type', accountType);
                formData.append('email', email);
                formData.append('password', password);
                formData.append('password2', password2);
                formData.append('age', age);
                formData.append('username', username);
                formData.append('api_key', api_key);
                formData.append('profile_name', fullname);

                const response = await fetch('http://localhost:8000/register/', {
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
                    console.log(data.errors)
                    if (data.errors) {
                        setError(data.errors);
                    } else {
                        setError({ submit: data.message });
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                setError(prev => ({ ...prev, submit: 'An error occurred during signup. Please try again.' }));
            } finally {
                setIsLoading(false);
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
                                        onChange={handleChange(setUsername, isValidUsername)}
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
                                        value={accountType}
                                        onChange={handleChange(setAccountType, isValidAccountType)}
                                    >
                                        <option value="0"></option>
                                        <option value="1">player</option>
                                        <option value="2">researcher</option>
                                    </select>
                                </div>
                                {error.accountType && <p className='Form-Error'>{error.accountType}</p>}
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
                                        onChange={handleChange(setEmail, isValidEmail)}
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
                                        onChange={handleChange(setPassword, isValidPassword)}
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
                                        onChange={handleChange(setPassword2, validatePasswords)}
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
                                        onChange={handleChange(setApiKey)}
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
                                        onChange={handleChange(setAge, isValidAge)}
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
                                        onChange={handleChange(setFullname, isValidFullName)}
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
                                <button className="App-Button" onClick={handleSignUpClick} disabled={isLoading}>
                                    {isLoading ? 'loading...' : 'sign up'}
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
