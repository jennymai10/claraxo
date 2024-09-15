import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import loginbuttom from './assets/login_button.png';
import signupbuttom from './assets/signup_button.png';
import loginbuttompressed from './assets/pencil.png';
import { BrowserRouter as Router, Route, Routes, useNavigate, Link } from 'react-router-dom';
// import playboard from './playboard';

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

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameVisible, setUsernameVisible] = useState(false);
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [ispressed, setIspressed] = useState(false);
  const navigate = useNavigate();

  // Function to handle changes in the username input field
  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };
  // Function to handle changes in the password input field
  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  // Show the username input field when clicked
  const handleUsernameClick = () => {
    setUsernameVisible(true);
  };

  // Show the password input field when clicked
  const handlePasswordClick = () => {
    setPasswordVisible(true);
  };

  const handleLoginPressed = () => {
    setIspressed(true);
  };

  const handleLoginRelease = () => {
    setIspressed(false);
  };

  // Function to handle login click event
  const handleLoginClick = async () => {
    const csrfToken = getCookie('csrftoken');  // Fetch CSRF token from cookies
    console.log('CSRF Token:', csrfToken);

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('http://localhost:8000/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        body: formData.toString(),
        credentials: 'include',
      });

      if (response.ok) {
        console.log('Login successful');
        navigate('/new_game');
      } else {
        console.log('Login failed');
        const result = await response.json();
        console.error('Failed to log in:', result);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Username:', username);
    console.log('Password:', password);
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={board} className="App-board" alt="board" />
        <img src={ruler} className="App-ruler" alt="ruler" />
        <img src={pencil} className="App-pencil" alt="pencil" />
        <div className="App-container">
          <div className="App-text">
            <p>tic. tac. toe.</p>
          </div>
          <div className='App-LoginForm'>
            <form onSubmit={handleSubmit}>
              <div className='App-UsernameQuery' onClick={handleUsernameClick}>
                <div className='App-UsernameText'>
                  <p>username</p>
                </div>
                <div className='App-UsernameRectangle'>
                  <input
                    type="text"
                    value={username}
                    onChange={handleUsernameChange}
                    placeholder=""
                    style={{ visibility: usernameVisible ? 'visible' : 'hidden' }}
                  />
                </div>
              </div>
              <div className='App-PasswordQuery' onClick={handlePasswordClick}>
                <div className='App-PasswordText'>
                  <p>password</p>
                </div>
                <div className='App-UPRectangle'>
                  <input
                    type="password"
                    value={password}
                    onChange={handlePasswordChange}
                    placeholder=""
                    style={{ visibility: passwordVisible ? 'visible' : 'hidden' }}
                  />
                </div>
              </div>
              <div className='App-LoginSignup'>
                <div className='App-or'>
                  <img
                    src={ispressed ? loginbuttompressed : loginbuttom}
                    className="App-loginbuttom"
                    alt="loginbuttom"
                    onMouseDown={handleLoginPressed}
                    onMouseUp={handleLoginRelease}
                    onClick={handleLoginClick}
                  />
                  <p>or</p>
                  <img
                    src={signupbuttom}
                    className="App-signupbuttom"
                    alt="signupbuttom"
                    onClick={() => navigate('/register')}
                  />
                </div>
              </div>
            </form>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;