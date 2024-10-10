import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';

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
  const [visibleMoves, setVisibleMoves] = useState({});
  const currentLocation = useLocation();
  const { games } = currentLocation.state || { games: [] };
  console.log(games);
  const csrfToken = getCookie('csrftoken');
  const [movesData, setMovesData] = useState([]);
  // Function to toggle the display of moves for a game
  const toggleMoves = async (gameId) => {
    setVisibleMoves((prev) => ({
      ...prev,
      [gameId]: !prev[gameId],
    }));
    try {
        const response = await fetch('http://127.0.0.1:8000/get_moves/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                'game_id': gameId
            }),
        })
        .then(response => response.json())
        .then(data => {
          if (data.moves) {
            console.log('Moves:', data.moves);
            setMovesData(data.moves)
          } else {
            console.error('Error fetching moves:', data.error);
          }
        });
    } catch (error) {
        console.error('Fetch error:', error);
    }
  };

  return (
    <div>
      <h1>Game History</h1>

      {games && games.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Game ID</th>
              <th>Player</th>
              <th>Date</th>
              <th>Winner</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game) => (
              <React.Fragment key={game.game_id}>
                <tr>
                  <td>{game.game_id}</td>
                  <td>{game.player}</td>
                  <td>{game.date}</td>
                  <td>{game.winner || "No winner yet"}</td>
                  <td>
                    <button onClick={() => toggleMoves(game.game_id)}>
                      {visibleMoves[game.game_id] ? 'Hide Moves' : 'Show Moves'}
                    </button>
                  </td>
                </tr>
                {visibleMoves[game.game_id] && (
                  <tr>
                    <td colSpan="5">
                      <table>
                        <thead>
                          <tr>
                            <th>Turn Number</th>
                            <th>Player</th>
                            <th>Move</th>
                            <th>Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {movesData.map((move) => (
                            <tr key={move.turn_number}>
                              <td>{move.turn_number}</td>
                              <td>{move.player}</td>
                              <td>{move.cell}</td>
                              <td>{move.timestamp}</td>
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
  );
};

export default GameHistory;
