import React, { useState } from 'react';
import board from './board.png';
import './App.css';
import ruler from './ruler.png';
import pencil from './pencil.png';
import loginbuttom from './LogIn button.png';
import signupbuttom from './Sign Up button.png';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameVisible, setUsernameVisible] = useState(false);
  const [passwordVisible, setPasswordVisible] = useState(false);

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleUsernameClick = () => {
    setUsernameVisible(true);
  };

  const handlePasswordClick = () => {
    setPasswordVisible(true);
  };

  // 处理登录按钮点击事件
  const handleLoginClick = async () => {
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
      } else {
        console.log('Login failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // 这里的表单提交可以是可选的，根据需要使用
    console.log('Username:', username);
    console.log('Password:', password);
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={board} className="App-board" alt="board" />
        <img src={ruler} className="App-ruler" alt="ruler" />
        <img src={pencil} className="App-pencil" alt="pencil" />
        {/* 添加点击事件处理器到图片 */}
        <img 
          src={loginbuttom} 
          className="App-loginbuttom" 
          alt="loginbuttom" 
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
            {/* 移除按钮，保持图片按钮 */}
          </form>
        </div>
      </header>
    </div>
  );
}

export default App;
