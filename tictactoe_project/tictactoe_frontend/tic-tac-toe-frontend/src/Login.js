import React, { useState } from 'react';
import board from './assets/board.png';
import './App.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { BrowserRouter as Router, Route, Routes, useNavigate, Link } from 'react-router-dom';

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
  const [error, setError] = useState({});
  const navigate = useNavigate();

  // Handle input changes and validate in real-time
  const handleChange = (setter, validateFn) => (event) => {
    setter(event.target.value);
    if (validateFn) validateFn(event.target.value);
  };

  // Validate username (5-15 characters, allows letters, numbers, '_', '-', and '.')
  const isValidUsername = (value) => {
    const usernamePattern = /^[A-Za-z0-9_.-]{4,15}$/;
    if (!usernamePattern.test(value)) {
        setError(prev => ({ ...prev, username: 'Username must be 5-15 characters long and can only contain letters, numbers, (_), (-), and (.).' }));
        return false;
    } else if (value === '') {
        return true
    }
    setError(prev => ({ ...prev, username: '' }));
    return true;
  };

  // Password strength check
  const isValidPassword = (value) => {
    const passwordPattern = /^(?=.*[A-Z])(?=.*\d).{6,25}$/;
    if (!passwordPattern.test(value)) {
        setError(prev => ({ ...prev, password: 'Password must be 7-25 characters long, with at least one uppercase letter and one number.' }));
        return false;
    } else if (value === '') {
        return true
    }
    setError(prev => ({ ...prev, password: '' }));
    return true;
  };

  // Function to handle login click event
  const handleLoginClick = async (event) => {
    event.preventDefault();
    setError({}); // Reset errors before validation
    if (
      isValidUsername(username) &&
      isValidPassword(password)
    ) {
      try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('http://localhost:8000/login/', {
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
          } else if (data.status === 'error') {
            setError(data.errors);
            setTimeout(() => {
              navigate(data.redirect_url);
            }, 6000);
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
          <div className="App-Title">
            <p>tic. tac. toe.</p>
          </div>
          <div className='App-LoginForm'>
            <form>
              <div className='App-Query'>
                <div className='App-NormalText'>
                  <p>username</p>
                </div>
                <div className='App-Rectangle'>
                  <input
                    type="text"
                    value={username}
                    onChange={handleChange(setUsername)}
                    placeholder=""
                    style={{}}
                  />
                </div>
                {/* {error.username && <p className='Form-Error'>{error.username}</p>} */}
              </div>
              <div className='App-Query'>
                <div className='App-NormalText'>
                  <p>password</p>
                </div>
                <div className='App-Rectangle'>
                  <input
                    type="password"
                    value={password}
                    onChange={handleChange(setPassword)}
                    placeholder=""
                    style={{}}
                  />
                </div>
                {/* {error.password && <p className='Form-Error'>{error.password}</p>} */}
              </div>
              {error.username && <p className='Form-Error'>{error.username}</p>}
              {error.password && <p className='Form-Error'>{error.password}</p>}
              {error.submit && <p className='Form-Error'>{error.submit}</p>}
              <div className='App-LoginSignup'>
                <div className='App-or'>
                  <button className="App-Button" onClick={handleLoginClick}> 
                  log in
                  </button>
                  <p className="App-Or-text">or</p>
                  <button className="App-Button" onClick={() => navigate('/signup')}> 
                  sign up
                  </button>
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