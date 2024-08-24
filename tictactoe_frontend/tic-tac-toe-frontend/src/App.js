import React, { useState } from 'react';
import board from './board.png';
import './App.css';
import ruler from './ruler.png';
import pencil from './pencil.png';
import loginbuttom from './LogIn button.png';
import signupbuttom from './Sign Up button.png';

function App() {
  // 创建状态来保存用户输入和输入框的可见性
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [usernameVisible, setUsernameVisible] = useState(false);
  const [passwordVisible, setPasswordVisible] = useState(false);

  // 处理用户名输入变化
  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  // 处理密码输入变化
  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  // 处理用户名点击事件
  const handleUsernameClick = () => {
    setUsernameVisible(true);
  };

  // 处理密码点击事件
  const handlePasswordClick = () => {
    setPasswordVisible(true);
  };

  // 处理表单提交（如果需要）
  const handleSubmit = (event) => {
    event.preventDefault();
    // 这里可以添加代码来处理提交，例如发送到服务器
    console.log('Username:', username);
    console.log('Password:', password);
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={board} className="App-board" alt="board" />
        <img src={ruler} className="App-ruler" alt="ruler" />
        <img src={pencil} className="App-pencil" alt="pencil" />
        <img src={loginbuttom} className="App-loginbuttom" alt="loginbuttom" />
        <img src={signupbuttom} className="App-signupbuttom" alt="signupbuttom" />
        <div className="App-text">
          <p>tic. tac. toe.</p>
        </div>
        <div className='App-LoginForm'>
          <form onSubmit={handleSubmit}>
            <div className='App-PasswordQuery' onClick={handlePasswordClick}>
              <div className='App-UPRectangle'>
                {/* 密码输入框 */}
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
                {/* 用户名输入框 */}
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
            <button type="submit" className="App-loginbuttom">
              Log In
            </button>
            <button type="button" className="App-signupbuttom">
              Sign Up
            </button>
          </form>
        </div>
      </header>
    </div>
  );
}

export default App;
