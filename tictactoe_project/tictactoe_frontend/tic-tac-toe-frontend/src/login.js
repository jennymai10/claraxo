import React, { useState } from 'react';
import board from './assets/board.png';
import './app.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { BrowserRouter as Router, Route, Routes, useNavigate, Link } from 'react-router-dom';


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

function Login() {
  const [username, set_username] = useState('');
  const [password, set_password] = useState('');
  const [is_loading, set_is_loading] = useState(false);
  const [error, set_error] = useState({});
  const navigate = useNavigate();

  // Handle input changes and validate in real-time
  const handle_change = (setter, validate_fn) => (event) => {
    setter(event.target.value);
    if (validate_fn) validate_fn(event.target.value);
  };

  // Validate username (5-15 characters, allows letters, numbers, '_', '-', and '.')
  const is_valid_username = (value) => {
    const username_pattern = /^[A-Za-z0-9_.-]{5,15}$/;
    if (!username_pattern.test(value)) {
      set_error(prev => ({ ...prev, username: 'Username must be 5-15 characters long and can only contain letters, numbers, (_), (-), and (.).' }));
      return false;
    } else if (value === '') {
      return true
    }
    set_error(prev => ({ ...prev, username: '' }));
    return true;
  };

  // Password strength check
  const is_valid_password = (value) => {
    const password_pattern = /^(?=.*[A-Z])(?=.*\d).{7,25}$/;
    if (!password_pattern.test(value)) {
      set_error(prev => ({ ...prev, password: 'Password must be 7-25 characters, with at least 1 uppercase letter and 1 number.' }));
      return false;
    } else if (value === '') {
      return true
    }
    set_error(prev => ({ ...prev, password: '' }));
    return true;
  };

  // Function to handle login click event
  const handle_login_click = async (event) => {
    set_is_loading(true);
    event.preventDefault();
    set_error({}); // Reset errors before validation
    if (
      is_valid_username(username) &&
      is_valid_password(password)
    ) {
      try {
        const form_data = new URLSearchParams();
        form_data.append('username', username);
        form_data.append('password', password);

        const response = await fetch(`${process.env.BACKEND_URL}/login/`, {
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
          console.log(data.errors)
          if (data.errors && data.redirect_url) {
            set_error(data.errors);
            setTimeout(() => {
              navigate(data.redirect_url);
            }, 3000);
          } else if (data.errors) {
            set_error(data.errors);

          } else {
            set_error({ submit: data.message });
          }
        }
      } catch (error) {
        console.error('Error:', error);
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
                    onChange={handle_change(set_username)}
                    placeholder=""
                    style={{}}
                  />
                </div>
              </div>
              <div className='App-Query'>
                <div className='App-NormalText'>
                  <p>password</p>
                </div>
                <div className='App-Rectangle'>
                  <input
                    type="password"
                    value={password}
                    onChange={handle_change(set_password)}
                    placeholder=""
                    style={{}}
                  />
                </div>
              </div>
              {error.username && <p className='Form-Error'>{error.username}</p>}
              {error.password && <p className='Form-Error'>{error.password}</p>}
              {error.submit && <p className='Form-Error'>{error.submit}</p>}
              <div className='App-LoginSignup'>
                <div className='App-or'>
                  <button className="App-Button" onClick={handle_login_click} disabled={is_loading}>
                    {is_loading ? 'loading...' : 'log in'}
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

export default Login;