import React, { useState, useEffect } from 'react';
import './app.css';
import SideTab from './sidetab';
import download from './assets/download_icon.png';

// Helper function to get CSRF token from cookies
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

const GameHistory = () => {
    const api_url = process.env.REACT_APP_API_URL;  // Fallback URL
    const [visibleMoves, setVisibleMoves] = useState({});
    const [movesData, setMovesData] = useState({});
    const [games, setGames] = useState([]); // Store the games fetched from the server
    const csrfToken = getCookie('csrftoken');

    // Fetch the game history when the component mounts
    useEffect(() => {
        const fetchGameHistory = async () => {
            try {
                const response = await fetch(`${api_url}/history/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    credentials: 'include'
                });
                const data = await response.json();
                setGames(data.games || []);  // Set the games state
            } catch (error) {
                console.error('Error fetching game history:', error);
            }
        };

        fetchGameHistory();
    }, [api_url, csrfToken]);

    const downloadGame = async (gameId) => {
        try {
            const response = await fetch(`${api_url}/game_log/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    'game_id': gameId
                }),
                credentials: 'include',
            });
    
            if (response.ok) {
                const data = await response.json();
                if (data.game_log) {
                    // Create a text file from the game log data
                    const blob = new Blob([data.game_log], { type: 'text/plain' });
                    const url = window.URL.createObjectURL(blob);
    
                    // Create an anchor element and trigger a download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `claraxo_log_${gameId}.txt`; // Sets the downloaded file's name
                    document.body.appendChild(a);
                    a.click();
    
                    // Clean up the temporary anchor element and object URL
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } else {
                    console.error('Error: No game log data found');
                }
            } else {
                console.error('Error response:', response);
            }
        } catch (error) {
            console.error('Fetch error:', error);
        }
    };    

    // Function to toggle the display of moves for a game
    const toggleMoves = async (gameId) => {
        setVisibleMoves((prev) => ({
            ...prev,
            [gameId]: !prev[gameId],
        }));
    
        // Fetch moves only if they haven't been fetched yet
        if (!movesData[gameId]) {
            try {
                const response = await fetch(`${api_url}/get_moves/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',  // Set the content type to JSON
                        'X-CSRFToken': csrfToken,  // Include CSRF token in the headers
                    },
                    body: JSON.stringify({
                        'game_id': gameId  // Send the game_id as JSON
                    }),
                    credentials: 'include',
                });
    
                // Parse the response as JSON
                const data = await response.json();
    
                if (response.ok) {
                    if (data.moves) {
                        // Store moves for the game in movesData state
                        setMovesData((prev) => ({
                            ...prev,
                            [gameId]: data.moves,
                        }));
                    } else {
                        console.error('Error fetching moves:', data.error);
                    }
                } else {
                    console.error('Error response:', data);
                }
            } catch (error) {
                console.error('Fetch error:', error);
            }
        }
    };    

    return (
        <div className="App">
            <div className="GameHistory">
                <SideTab user="username" />
                <div style={{fontFamily: 'Londrina Shadow', fontSize: '3rem', letterSpacing: '0.15rem', textAlign: 'center'}}>
                    <h4>game history</h4>
                </div>

                {games.length > 0 ? (
                    <table className="game-table">
                        <thead>
                            <tr>
                                <th>game id</th>
                                <th>date & time</th>
                                <th>level</th>
                                <th>completed</th>
                                <th>winner</th>
                                <th>game moves</th>
                                <th>export</th>
                            </tr>
                        </thead>
                        <tbody>
                            {games.map((game) => (
                                <React.Fragment key={game.game_id}>
                                    <tr>
                                        <td>{game.game_id}</td>
                                        <td>
                                        {new Date(game.date).toLocaleDateString([], { day: '2-digit', month: '2-digit', year: 'numeric' })}{" @ "}
                                        {new Date(game.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </td>
                                        <td>{game.ai_difficulty}</td>
                                        <td>{game.completed ? "yes" : "no"}</td>
                                        <td>{game.winner || "no winner"}</td>
                                        <td>
                                            <button className="Small-Button" onClick={() => toggleMoves(game.game_id)}>
                                                {visibleMoves[game.game_id] ? 'hide' : 'show'}
                                            </button>
                                        </td>
                                        <td>
                                            <img
                                                src={download}
                                                className="edit-icon"
                                                style={{ cursor: 'pointer', paddingTop: '0.5rem' }}
                                                alt="download"
                                                onClick={() => downloadGame(game.game_id)}
                                            />
                                        </td>
                                    </tr>
                                    {visibleMoves[game.game_id] && movesData[game.game_id] && (
                                        <tr>
                                            <td colSpan="7">
                                                <table className="moves-table">
                                                    <thead>
                                                        <tr>
                                                            <th>turn number</th>
                                                            <th>player</th>
                                                            <th>turn</th>
                                                            <th>move</th>
                                                            <th>date & time</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {movesData[game.game_id].map((move) => (
                                                            <tr key={move.turn_number}>
                                                                <td>{move.turn_number}</td>
                                                                <td>{move.player}</td>
                                                                <td>{move.player === "X" ? "you" : "AI"}</td>
                                                                <td>{move.cell}</td>
                                                                <td>
                                                                {new Date(move.timestamp).toLocaleDateString([], { day: '2-digit', month: '2-digit', year: 'numeric' })}{" @ "}
                                                                {new Date(move.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No completed games found.</p>
                )}
            </div>
        </div>
    );
};

export default GameHistory;