import React, { useState } from 'react';
import './App.css';
import icon from './assets/icon.png';
import { BrowserRouter as Router, Route, Routes, useNavigate, Link } from 'react-router-dom';
import vector from './assets/Vector.png';
import history from './assets/History.png';
import setting from './assets/Setting.png';
// $env:API_KEY = "AIzaSyCIpXn9AisIMSBfisG1U63XaSjmIPgC_dU"
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

export function SideTab({ user }) {
    const csrfToken = getCookie('csrftoken');
    const formData = new URLSearchParams();
    const formHistory = new URLSearchParams();
    const [isOpen, setIsOpen] = useState(false);
    const [iconLocation, setIconLocation] = useState({ top: 40, right: 360 });
    const [accountType, setaccountType] = useState('');
    const navigate = useNavigate();
    let games = [];
    formData.append('username', user);
    formHistory.append('username',user);


    const handleLogout = async () => {
      try {
          const response = await fetch('http://localhost:8000/logout/', {
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



    const toggleSideTab = async () => {

        try {
            const response = await fetch('http://localhost:8000/get_user_type/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
              },
              body: formData.toString(),
              credentials: 'include',
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                if(data.account_type === 1){
                    setaccountType('Player');
                    console.log(accountType);
                }else{
                    setaccountType('Reacher');
                }
            } else {
                console.error('Error:', data.message);
            }

          } catch (error) {
            console.error('Error:', error);
          }


        setIsOpen(!isOpen);
        setIconLocation(isOpen ? { top: 40, right: 360 } : { top: 40, right: 262 });
    };

    const handnewgame = async () => {
      navigate('/playboard');
    }

    const gamehistory = async () =>{
      try {
        const response = await fetch('http://localhost:8000/history/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
          },
          body: formHistory.toString(),
          credentials: 'include',
        });
        const data = await response.json();
        games = data.games
        console.log(games)

          
        navigate('/gamehistory', { state: { games } });


      } catch (error) {
        console.error('Error:', error);
      }
    }

    return (
        <>
            <div className={`side-tab ${isOpen ? 'active' : ''}`}>
                {/* Side tab content */}
                <img 
                    src={icon} 
                    className='Icon' 
                    alt='icon' 
                    onClick={toggleSideTab} 
                    style={{ top: iconLocation.top, right: iconLocation.right }}
                />
                <div className='Title'>
                    <p>Tic Tac Toe</p>
                    <p>
                      welcome ! <br />
                      <br />
                      {user}<br />
                      <span className="account-type">{accountType}</span>
                    </p>
                    
                </div>


                
                <div className='sidetab-text'onClick={handnewgame}>
                <p>New Game</p>
                </div>
                <img className='vector' src={vector}/>


                <div className='sidetab-text' onClick={gamehistory}>
                <p>History</p>
                </div>
                <img className='vector' src={history}/>

                <div className='sidetab-text'>
                <p>Seeting</p>
                </div>
                <img className='vector' src={setting}/>

                <button className="logout-btn" onClick={handleLogout}>
                    Logout
                </button>
                
            </div>
        </>
    );
}
