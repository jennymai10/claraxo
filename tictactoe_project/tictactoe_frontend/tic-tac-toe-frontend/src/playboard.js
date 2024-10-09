import React, { useState, useEffect } from 'react';
import './app.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import board from './assets/board.png';
import SideTab from './sidetab';

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

const TicTacToe = () => {
    const api_url = process.env.REACT_APP_API_URL;
    const [isO, setisO] = useState(false);  // Track current player
    const [x_location, setxlocation] = useState([]); 
    const [o_location, setolocation] = useState([]); 
    const [winner, setWinner] = useState('Game not start');
    const [winmove, setwinmove] = useState([]);
    const [error, set_error] = useState({});
    const [isWaitingForAI, setIsWaitingForAI] = useState(false);  // Track if waiting for AI

    const handleClick = async (event) => {
        if (winner !== 'Game not start' || isWaitingForAI) return; // Prevent clicks if the game is over or waiting for AI

        const id = event.target.id;

        // Check if the clicked square is valid and proceed
        if (!isO) {  // X's turn
            // Update UI with player's move (X)
            event.target.textContent = 'X';
            setxlocation(prev => [...prev, id]); // Store the move in the state
            event.target.disabled = true;

            // Disable all buttons while waiting for the AI move
            setIsWaitingForAI(true);
            disableAllButtons();

            const move_data = new URLSearchParams();
            move_data.append('move', id);

            // Send the move to the backend for processing
            try {
                const response = await fetch(`${api_url}/make_move/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),  // CSRF token handling
                    },
                    credentials: 'include',
                    body: move_data.toString(),
                });

                const data = await response.json();
                if (data.status === 'success') {
                    if (data.errors) {
                        set_error(data.errors);
                    }
                    // AI's move (O) from the backend
                    const aiMove = data.ai_move;

                    // Find the corresponding button for the AI's move and update it
                    const aiButton = document.getElementById(aiMove);
                    if (aiButton) {
                        aiButton.textContent = 'O';
                        aiButton.disabled = true;
                        setolocation(prev => [...prev, aiMove]);  // Store AI's move in the state
                    }

                    // Enable buttons after AI move is processed
                    enableAllButtons();
                    setIsWaitingForAI(false);  // Reset waiting flag

                } else {
                    console.error('Error:', data.message);  // Handle error if any
                    setIsWaitingForAI(false);  // Reset if an error occurs
                    enableAllButtons();
                }
            } catch (error) {
                console.error('Error:', error);  // Catch and log any errors during the API request
                setIsWaitingForAI(false);  // Reset waiting flag on error
                enableAllButtons();
            }
        }
    };

    const disableAllButtons = () => {
        const buttons = document.querySelectorAll('.square');
        buttons.forEach(button => {
            if (!button.textContent) {
                button.disabled = true;
            }
        });
    };

    const enableAllButtons = () => {
        const buttons = document.querySelectorAll('.square');
        buttons.forEach(button => {
            if (!button.textContent) {
                button.disabled = false;
            }
        });
    };

    // Check if there is a winner after each state update
    useEffect(() => {
        if (checkWinner(x_location)) {
            setWinner('X');
        } else if (checkWinner(o_location)) {
            setWinner('O');
        }
    }, [x_location, o_location]);

    useEffect(() => {
        // Highlight winning move
        if (winner !== 'Game not start') {
            highlightWinningMove();
        }
    }, [winner]);

    // Check if there is a winner
    const checkWinner = (locations) => {
        const winPatterns = [
            ['a1', 'a2', 'a3'], 
            ['b1', 'b2', 'b3'], 
            ['c1', 'c2', 'c3'], 
            ['a1', 'b1', 'c1'], 
            ['a2', 'b2', 'c2'], 
            ['a3', 'b3', 'c3'], 
            ['a1', 'b2', 'c3'], 
            ['a3', 'b2', 'c1']  
        ];
    
        for (let pattern of winPatterns) {
            if (pattern.every(pos => locations.includes(pos))) {
                setwinmove(pattern);
                return true;
            }
        }
        return false;
    };

    // Highlight winning move
    const highlightWinningMove = () => {
        const winbuttons = document.querySelectorAll('.square');
        winbuttons.forEach(button => {
            if (winmove.includes(button.id)) {
                button.style.backgroundColor = '#f9f0e1';
            }
        });
    };

    // Reset game state
    const handleStart = () => {
        setisO(false);  // Player starts as X
        setxlocation([]);
        setolocation([]);
        setWinner('Game not start');
        setwinmove([]);
        const buttons = document.querySelectorAll('.square');
        buttons.forEach(button => {
            button.textContent = '';
            button.disabled = false;
            button.style.backgroundColor = '';
        });
    };

    // Determine the status message to display
    const getStatusMessage = () => {
        if (winner === 'X') return "Player X wins!";
        if (winner === 'O') return "AI O wins!";
        if (isWaitingForAI) return "O's thinking...";  // Display while waiting for AI
        return "X's turn";  // Default when waiting for player
    };

    return (
        <div className="App">
            <header className="App-header">
                <SideTab user="username" />
                <img src={board} className="App-board" draggable="false" />
                <img src={ruler} className="App-ruler" draggable="false" />
                <img src={pencil} className="App-pencil" draggable="false" />
                <div className='Playboard-container'>
                    <div>
                        <div className='Playboard-NormalText' text-align='center'> 
                            <p>{getStatusMessage()}</p>  {/* Status message based on game state */}
                        </div>
                        <div className="Playboard">
                            {error.all && <p className='Form-Error' style={{marginBottom: '1rem'}}>{error.all}</p>}
                            <div className="row">
                                <button className="square" id="a3" onClick={handleClick}></button>
                                <button className="square" id="b3" onClick={handleClick}></button>
                                <button className="square" id="c3" onClick={handleClick}></button>
                            </div>
                            <div className="row">
                                <button className="square" id="a2" onClick={handleClick}></button>
                                <button className="square" id="b2" onClick={handleClick}></button>
                                <button className="square" id="c2" onClick={handleClick}></button>
                            </div>
                            <div className="row">
                                <button className="square" id="a1" onClick={handleClick}></button>
                                <button className="square" id="b1" onClick={handleClick}></button>
                                <button className="square" id="c1" onClick={handleClick}></button>
                            </div>
                        </div>
                        <button className="App-Button" onClick={handleStart}>restart game</button>
                    </div>
                </div>
            </header>
        </div>
    );
};

export default TicTacToe;
