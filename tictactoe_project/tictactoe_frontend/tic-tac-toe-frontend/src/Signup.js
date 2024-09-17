import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import signupbuttom from './assets/signup_button.png';

import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';


function Signup() {
    const [accountType, setAccountType] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [rePassword, setRePassword] = useState('');
    const [usernameVisible, setUsernameVisible] = useState(false);
    const [accountTypeVisible, setAccountTypeVisible] = useState(false);
    const [passwordVisible, setPasswordVisible] = useState(false);
    const [rePasswordVisible, setRePasswordVisible] = useState(false);
    const [ispressed, setIspressed] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    // Function to handle changes in the username input field
    const handleUsernameChange = (event) => {
        setUsername(event.target.value);
    };
    const handleAccountTypeChange = (event) => {
        setAccountType(event.target.value);
    };
    // Function to handle changes in the password input field
    const handlePasswordChange = (event) => {
        setPassword(event.target.value);
    };

    const handleRePasswordChange = (event) => {
        setRePassword(event.target.value);
    };

    // Show the username input field when clicked
    const handleUsernameClick = () => {
        setUsernameVisible(true);
    };

    const handleAccountTypeClick = () => {
        setAccountTypeVisible(true);
    };

    // Show the password input field when clicked
    const handlePasswordClick = () => {
        setPasswordVisible(true);
    };

    const handleRePasswordClick = () => {
        setRePasswordVisible(true);
    };

    const handleLoginPressed = () => {
        setIspressed(true);
    };

    const handleLoginRelease = () => {
        setIspressed(false);
    };

    // Handle the login button click event
    const handleLoginClick = async () => {
        console.log('Login button clicked');
        try {
            const response = await fetch('http://127.0.0.1:8000/tictactoe/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accountType: accountType,
                    username: username,
                    password: password,
                    rePassword: rePassword,
                }),
            });

            if (response.ok) {
                console.log('Login successful');
                navigate('/playboard');
            } else {
                console.log('Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };
    const handleSignUpClick = async () => {
        console.log('SignUp button clicked');
        if (password !== rePassword) {
            //setPassword('');
            //setRePassword('');
            setError('The passwords entered twice do not match. Please re-enter');
            return;
        }
        setError('');
        try {
            const response = await fetch('http://127.0.0.1:8000/tictactoe/signUp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accountType: accountType,
                    username: username,
                    password: password,
                }),
            });

            if (response.ok) {
                console.log('Login successful');
                navigate('/playboard');
            } else {
                console.log('Login failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log('accountType:', accountType);
        console.log('Username:', username);
        console.log('Password:', password);
        console.log('rePassword:', rePassword);
    };

    return (
        <div className="Signup">
            <header className="Signup-header">
                <img src={board} className="Signup-board" alt="board" />
                <img src={ruler} className="Signup-ruler" alt="ruler" />
                <img src={pencil} className="Signup-pencil" alt="pencil" />
                <img
                    src={signupbuttom}
                    className="Signup-signupbuttom"
                    alt="signupbuttom"
                    onClick={handleSignUpClick}
                />
                <div className='Signup-LoginForm'>
                    <form onSubmit={handleSubmit}>
                        <div>
                            <div className='Signup-AccountTypeRectangle'>
                                <select className='Signup-AccountTypeRectangle' onChange={handleAccountTypeChange} value={accountType}>

                                    <option value="1">student</option>
                                    <option value="2">teacher</option>
                                    <option value="3">admin</option>

                                </select>
                            </div>
                            <div className='Signup-AccountTypeText'>
                                <p>Account type</p>
                            </div>
                        </div>
                        <div className='Signup-UsernameQuery'>
                            <div className='Signup-UernameRectangle' onClick={handleUsernameClick}>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={handleUsernameChange}
                                    placeholder=""
                                    style={{ visibility: usernameVisible ? 'visible' : 'hidden' }}
                                />
                            </div>
                            <div className='Signup-UsernameText'>
                                <p>Username/Email</p>
                            </div>
                        </div>
                        <div className='Signup-PasswordQuery' onClick={handlePasswordClick}>
                            <div className='Signup-UPRectangle'>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={handlePasswordChange}
                                    placeholder=""
                                    style={{ visibility: passwordVisible ? 'visible' : 'hidden' }}
                                />
                            </div>
                            <div className='Signup-PasswordText'>
                                <p>Password</p>
                            </div>
                        </div>
                        <div className='Signup-UsernameQuery' onClick={handleRePasswordClick}>
                            <div className='Signup-REUPRectangle'>
                                <input
                                    type="password"
                                    value={rePassword}
                                    onChange={handleRePasswordChange}
                                    placeholder=""
                                    style={{ visibility: rePasswordVisible ? 'visible' : 'hidden' }}
                                />
                            </div>
                            <div className='Signup-RePasswordText'>
                                <p>re-enter password:</p>
                            </div>
                        </div>
                        <div className='Signup-errorMsgText'>
                            {error && <p style={{ color: 'red' }}>{error}</p>}
                        </div>

                        <div className='Signup-signupbuttom'>

                        </div>
                        {/* Removed buttons, kept the image buttons */}
                    </form>
                </div>
            </header>
        </div>
    );
}

export default Signup;
