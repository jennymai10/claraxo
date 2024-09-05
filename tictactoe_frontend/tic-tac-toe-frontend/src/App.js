import React, { useState } from 'react';
import board from './board.png';
import './App.css';
import ruler from './ruler.png';
import pencil from './pencil.png';
import loginbuttom from './LogIn button.png';
import signupbuttom from './Sign Up button.png';
import loginbuttompressed from'./LogIn button_white.png';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import playboard from './playboard';

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

  const handleLoginPressed =() =>{
    setIspressed(true);
  };

  const handleLoginRelease =() =>{
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
    console.log('Username:', username);
    console.log('Password:', password);
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={board} className="App-board" alt="board" />
        <img src={ruler} className="App-ruler" alt="ruler" />
        <img src={pencil} className="App-pencil" alt="pencil" />
        {/* Add click event handler to the sign-up button */}
        <img 
          src={ispressed ? loginbuttompressed : loginbuttom } 
          className= "App-loginbuttom"
          alt="loginbuttom" 
          onMouseDown={handleLoginPressed}
          onMouseUp={handleLoginRelease}
          onClick={handleLoginClick}
        />
        <img 
          src={signupbuttom} 
          className="App-signupbuttom" 
          alt="signupbuttom" 
          onClick={() => console.log('Sign Up clicked')} 
        />
        <div className="App-text">
          <p>tic. tac. toe.</p>
        </div>
        <div className='App-LoginForm'>
          <form onSubmit={handleSubmit}>
            <div className='App-PasswordQuery' onClick={handlePasswordClick}>
              <div className='App-UPRectangle'>
                <input
                  type="password"
                  value={password}
                  onChange={handlePasswordChange}
                  placeholder=""
                  style={{ visibility: passwordVisible ? 'visible' : 'hidden' }}
                />
              </div>
              <div className='App-PasswordText'>
                <p>Password</p>
              </div>
            </div>
            <div className='App-UsernameQuery' onClick={handleUsernameClick}>
              <div className='App-UernameRectangle'>
                <input
                  type="text"
                  value={username}
                  onChange={handleUsernameChange}
                  placeholder=""
                  style={{ visibility: usernameVisible ? 'visible' : 'hidden' }}
                />
              </div>
              <div className='App-UsernameText'>
                <p>Username/Email</p>
              </div>
            </div>
            <div className='App-LoginSignup'>
              <div className='App-or'>
                <p>or</p>
              </div>
            </div>
            {/* Removed buttons, kept the image buttons */}
          </form>
        </div>
      </header>
    </div>
  );
}

export default App;
