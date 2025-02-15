import React, { useState, useEffect } from 'react';
import icon from './assets/icon.png'; // Assuming the icon is part of the assets
import icon2 from './assets/icon2.svg';
import newgame_icon from './assets/newgame_icon.png';
import gamehistory_icon from './assets/gamehistory_icon.png';
import settings_icon from './assets/settings_icon.png';
import './app.css'; // Reuse your existing CSS file
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

const SideTab = ({ user }) => {
  const api_url = process.env.REACT_APP_API_URL;
  const [isOpen, setIsOpen] = useState(false);
  const [accountType, setAccountType] = useState('');
  const [username, setUsername] = useState('');
  const csrfToken = getCookie('csrftoken');
  const navigate = useNavigate();

  useEffect(() => {
    if (accountType==='' && username==='') {
      // Fetch the account type when the side-tab opens
      fetchAccountType();
    }
  }, [isOpen]);

  const fetchAccountType = async () => {
    try {
      const response = await fetch(`${api_url}/get_user/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        if (!data.username) {
          navigate('/login');
          return;
        }
        setAccountType(data.account_type === 2 ? 'researcher' : 'player');
        setUsername(data.username);
      } else {
        console.error('Error fetching user data:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  

  const handleLogout = async () => {
    try {
      const response = await fetch(`${api_url}/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        credentials: 'include',
      });

      if (response.ok) {
        navigate('/login');
      } else {
        console.error('Logout failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const toggleSideTab = () => {
    setIsOpen(!isOpen);
  };

  const handleNewGame = async () => {
    navigate('/new_game');
    window.location.reload(); 
  };


  const handleHistory = () => {
    navigate('/history');
  };

  const handleSettings = () => {
    navigate('/settings');
  };

  return (
    <div>
      {/* Sidebar toggle icon */}
      <img
        src={isOpen ? icon2 : icon}
        alt="Toggle SideTab"
        className="Icon"
        style={{ position: 'absolute', top: '1rem', right: '0.6rem'}}
        draggable="false"
        onClick={toggleSideTab}
      />
      <div className={`side-tab ${isOpen ? 'active' : ''}`}>
        {isOpen && (
          <div>
            <div className="App-FormName">
              <h4 style={{ fontSize: '1.6rem', textAlign: 'center', margin: 0, marginRight: '3rem' }}>ClaraXO</h4>
            </div>
            <div className="App-NormalText" style={{textAlign: 'left', marginTop: '5vh', marginBottom: '10vh'}}>
              <p style={{textAlign: 'center'}}>
                welcome, {username}!
              </p>
              <p style={{textAlign: 'center'}}>
                - {accountType} -
              </p>
              <div style={{marginTop: '10vh', marginBottom: '5vh', marginLeft: '2rem', cursor: 'pointer'}} onClick={handleNewGame}>
                <p><img
                  draggable="false"
                  src={newgame_icon}
                  style={{ marginRight: '0.75rem', width: '1.25rem', height: 'auto' }}
                />
                new game</p>
              </div>
              <div style={{marginBottom: '5vh', marginLeft: '2rem', cursor: 'pointer'}} onClick={handleHistory}>
                <p><img
                  src={gamehistory_icon}
                  draggable="false"
                  style={{ marginRight: '0.75rem', width: '1.25rem', height: 'auto' }}
                />game history</p>
              </div>
              <div style={{marginBottom: '5vh', marginLeft: '2rem', cursor: 'pointer'}} onClick={handleSettings}>
                <p><img
                  src={settings_icon}
                  draggable="false"
                  style={{ marginRight: '0.75rem', width: '1.25rem', height: 'auto' }}
                />settings</p>
              </div>
            </div>
            <div style={{}}>
              <button className="App-Button" onClick={handleLogout}>logout</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SideTab;