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
    const [x_location, setxlocation] = useState([]);  // Track X's moves
    const [o_location, setolocation] = useState([]);  // Track O's moves
    const [winner, setWinner] = useState('Game not start');
    const [winmove, setwinmove] = useState([]);
    const [error, set_error] = useState({});
    const [isWaitingForAI, setIsWaitingForAI] = useState(false);  // Track if waiting for AI
    const [logs, setLogs] = useState([]);  // Log entries for terminal
    const [isResearcher, setIsResearcher] = useState(false);  // Track if the user is a researcher

    useEffect(() => {
        handleStart();  // Automatically start a new game on mount
        fetchUser();  // Fetch user data to check if they are a researcher
    }, []);

    // Function to add logs to the terminal
    const addLog = (message) => {
        setLogs((prevLogs) => [...prevLogs, message]);
    };

    // Fetch user data to check if they are a researcher
    const fetchUser = async () => {
        try {
            const response = await fetch(`${api_url}/get_user/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                credentials: 'include',
            });

            const data = await response.json();
            if (response.ok && data.account_type === 2) {
                setIsResearcher(true);  // User is a researcher
            } else {
                setIsResearcher(false);  // User is not a researcher
            }
        } catch (error) {
            console.error('Error fetching user data:', error);
        }
    };

    const handleClick = async (event) => {
        if (winner !== 'Game not start' || isWaitingForAI) return;

        const id = event.target.id;

        addLog(`[INFO] Player clicked square ${id}`);

        if (!isO) {
            event.target.textContent = 'X';
            setxlocation(prev => [...prev, id]);  // Store the move in the state
            event.target.disabled = true;

            setIsWaitingForAI(true);
            disableAllButtons();

            const move_data = new URLSearchParams();
            move_data.append('move', id);

            addLog(`[INFO] Sending player's move to AI...`);

            try {
                const response = await fetch(`${api_url}/make_move/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    credentials: 'include',
                    body: move_data.toString(),
                });

                const data = await response.json();

                if (data.status === 'success') {
                    if (data.errors) {
                        set_error(data.errors);
                    }

                    const aiMove = data.ai_move;
                    addLog(`[INFO] AI's move: ${aiMove}`);
                    
                    // Log the prompt and AI response for research purposes
                    if (data.prompt_log) {
                        addLog(`[PROMPT] ${data.prompt_log}`);
                    }
                    if (data.ai_response_log) {
                        addLog(`[RESPONSE] ${data.ai_response_log}`);
                    }

                    const aiButton = document.getElementById(aiMove);
                    if (aiButton) {
                        aiButton.textContent = 'O';
                        aiButton.disabled = true;
                        setolocation(prev => [...prev, aiMove]);
                    }

                    enableAllButtons();
                    setIsWaitingForAI(false);

                } else {
                    console.error('Error:', data.message);
                    addLog(`[ERROR] ${data.message}`);
                    setIsWaitingForAI(false);
                    enableAllButtons();
                }
            } catch (error) {
                console.error('Error:', error);
                addLog(`[ERROR] ${error.message}`);
                setIsWaitingForAI(false);
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
            addLog("[INFO] Player X wins!");
        } else if (checkWinner(o_location)) {
            setWinner('O');
            addLog("[INFO] AI O wins!");
        }
    }, [x_location, o_location]);

    // Highlight winning move
    useEffect(() => {
        if (winner !== 'Game not start') {
            highlightWinningMove();
        }
    }, [winner]);

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

    const highlightWinningMove = () => {
        const winbuttons = document.querySelectorAll('.square');
        winbuttons.forEach(button => {
            if (winmove.includes(button.id)) {
                button.style.backgroundColor = '#f9f0e1';
            }
        });
    };

    const handleStart = async () => {
        try {
            const response = await fetch(`${api_url}/new_game/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                credentials: 'include',
            });

            const data = await response.json();

            if (response.ok) {
                setisO(false);  // Player starts as X
                setxlocation([]);
                setolocation([]);
                setLogs([]);
                setWinner('Game not start');
                setwinmove([]);
                addLog("[INFO] Game started");

                // Reset the board UI
                const buttons = document.querySelectorAll('.square');
                buttons.forEach(button => {
                    button.textContent = '';
                    button.disabled = false;
                    button.style.backgroundColor = '';
                });
            } else {
                console.error('Error resetting game:', data.message);
                addLog(`[ERROR] ${data.message}`);
            }
        } catch (error) {
            console.error('Error:', error);
            addLog(`[ERROR] ${error.message}`);
        }
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
                <img src={board} className="App-board" draggable="false" alt="Board" />
                <img src={ruler} className="App-ruler" draggable="false" alt="Ruler" />
                <img src={pencil} className="App-pencil" draggable="false" alt="Pencil" />
                <div className='Playboard-container'>
                    <div>
                        <div className='Playboard-NormalText' style={{ textAlign: 'center' }}>
                            <p>{getStatusMessage()}</p>  {/* Status message based on game state */}
                        </div>
                        <div className="Playboard">
                            {error.all && <p className='Form-Error' style={{ marginBottom: '1rem' }}>{error.all}</p>}
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
                        <button className="App-Button" onClick={handleStart}>restart</button>
                    </div>
                    {/* Logging panel, visible only for researchers */}
                    {isResearcher && (
                        <div className="logging-panel">
                            <h3>Terminal</h3>
                            <div className="log-entries">
                                {logs.map((log, index) => (
                                    <div key={index} className="log-entry">{log}</div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </header>
        </div>
    );
};

export default TicTacToe;