import React, { useState, useEffect } from 'react';
import './App.css';
import TicBoard from './assets/TicBoard.png'
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import board from './assets/board.png';

import { SideTab } from './SideTab';
import { useLocation } from 'react-router-dom';
const TicTacToe = () => {
    const [isO, setisO] = useState(true);
    const [x_location, setxlocation] = useState([]); 
    const [o_location, setolocation] = useState([]); 
    const [winner, setWinner] = useState('Game not start');
    const [winmove, setwinmove] = useState([]);
    const location = useLocation();
    const username = location.state?.username;

    // Handle click events for game buttons
    const handleClick = async (event) => {
    if (winner !== 'Game not start') return;

    const id = event.target.id;

    if (isO) {
        event.target.textContent = 'O';
        setisO(false);
        setolocation(prev => [...prev, id]);
        
        try {
            const response = await fetch('http://127.0.0.1:8000/make_move/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'move': id
                }),
            });
            
            // const data = await response.json();
            // console.log('AI move response:', data); // 查看响应数据

            // // Assuming AI move is in data.ai_move
            // const cellElement = document.getElementById('square' + data.ai_move);
            // if (cellElement) {
            //     cellElement.innerText = 'X';
            // }
        } catch (error) {
            console.error('Fetch error:', error);
        }
    } else {
        event.target.textContent = 'X';
        setisO(true);
        setxlocation(prev => [...prev, id]);
    }

    event.target.disabled = true;
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
                button.style.backgroundColor = 'black';
            }
        });
    };

    // Reset game state
    const handleStart = () => {
        setisO(true);
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

    return (
        <div>
            <img className='TicBoard' src={TicBoard}></img>
            <img src={board} className="Bboard" alt="board" />
            <img src={ruler} className="Ruler" alt="ruler" />
            <img src={pencil} className="Pencil" alt="pencil" />
            <SideTab />
            <div className='Moves'> 
                <p>{isO ? "O's turn" : "X's turn"}</p>
            </div>
            <div id="board">
                <button className="square" id="a3" onClick={handleClick}></button>
                <button className="square" id="b3" onClick={handleClick}></button>
                <button className="square" id="c3" onClick={handleClick}></button>
                <button className="square" id="a2" onClick={handleClick}></button>
                <button className="square" id="b2" onClick={handleClick}></button>
                <button className="square" id="c2" onClick={handleClick}></button>
                <button className="square" id="a1" onClick={handleClick}></button>
                <button className="square" id="b1" onClick={handleClick}></button>
                <button className="square" id="c1" onClick={handleClick}></button>
            </div>
            <button className="start-button" onClick={handleStart}>Start Game</button>
            {username && <SideTab user={username} />}
        </div>
    );
};

export default TicTacToe;
