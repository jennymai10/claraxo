import { render, screen, fireEvent } from '@testing-library/react';
import Login from './login';
import { BrowserRouter } from 'react-router-dom';

process.env.REACT_APP_SECRET_KEY = 'your-test-secret-key';
process.env.REACT_APP_API_URL = 'http://localhost:8000';

jest.mock('crypto-js', () => ({
  AES: {
    encrypt: jest.fn().mockReturnValue({
      ciphertext: { toString: () => 'encrypted' },
    }),
  },
  enc: {
    Base64: {
      parse: jest.fn(),
    },
    Utf8: {},
  },
  lib: {
    WordArray: {
      random: jest.fn(() => 'random_iv'),
    },
  },
  pad: { Pkcs7: {} },
  mode: { CBC: {} },
}));

test('renders Login component and submits form', async () => {
  // Render the Login component wrapped in the BrowserRouter for routing support
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  // Check if the username and password fields are rendered by their id
  const usernameInput = screen.getByRole('textbox', { id: 'username' });
  const passwordInput = screen.getByRole('textbox', { id: 'password' });

  // Simulate typing a username and password
  fireEvent.change(usernameInput, { target: { value: 'testuser' } });
  fireEvent.change(passwordInput, { target: { value: 'TestPassword123' } });

  // Check if the login button is rendered
  const loginButton = screen.getByRole('button', { name: /log in/i });
  expect(loginButton).toBeInTheDocument();

  // Simulate click on login button
  fireEvent.click(loginButton);

  // Ensure fetch was called with the expected values
  expect(global.fetch).toHaveBeenCalledWith(
    'http://localhost:8000/login/',
    expect.objectContaining({
      method: 'POST',
    })
  );
});