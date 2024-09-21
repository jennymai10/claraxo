import React, { useState } from 'react';

function VerifyEmail() {
  const [username, setUsername] = useState('');
  const [code, setCode] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleVerify = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/verify_email/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, code }),
      });

      if (response.ok) {
        // Redirect to login page
        window.location.href = '/login';
      } else {
        setErrorMessage('Invalid code or username.');
      }
    } catch (error) {
      setErrorMessage('Verification failed.');
    }
  };

  return (
    <form onSubmit={handleVerify}>
      <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required />
      <input type="text" value={code} onChange={(e) => setCode(e.target.value)} placeholder="Verification Code" required />
      {errorMessage && <p>{errorMessage}</p>}
      <button type="submit">Verify</button>
    </form>
  );
}

export default VerifyEmail;