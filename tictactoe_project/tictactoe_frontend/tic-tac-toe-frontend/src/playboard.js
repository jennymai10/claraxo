import React, { useState } from 'react';
import './playboard.css';

const TicTacToe = () => {
    const [board, setBoard] = useState(Array(9).fill(null)); // 初始化棋盘状态
    const [isXNext, setIsXNext] = useState(true); // 用来记录下一个是 "X" 还是 "O"

    const handleClick = (event) => {
        const id = parseInt(event.target.id); // 获取点击按钮的 id

        if (board[id]) return; // 如果该位置已经被点击过，直接返回

        const newBoard = [...board];
        newBoard[id] = isXNext ? 'X' : 'O'; // 根据 isXNext 决定填入 "X" 还是 "O"
        setBoard(newBoard); // 更新棋盘状态
        setIsXNext(!isXNext); // 切换到另一个玩家

        // 可选：在这里禁用按钮，确保无法再次点击
        event.target.disabled = true;
    };

    return (
        <div id="board">
            {board.map((value, index) => (
                <button
                    key={index}
                    id={index}
                    className="square"
                    onClick={handleClick}
                >
                    {value}
                </button>
            ))}
        </div>
    );
};

export default TicTacToe;
