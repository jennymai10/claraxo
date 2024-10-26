import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Login from './login';
import { BrowserRouter } from 'react-router-dom';

test('renders Login component and submits form', async () => {
  // Render the Login component wrapped in the BrowserRouter for routing support
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  // Check if the username and password fields are rendered
  const usernameInput = screen.getByRole('textbox', { id: 'username' });
  const passwordInput = screen.getByRole('textbox', { id: 'password' });

  // Simulate typing a valid username and password that passes validation
  fireEvent.change(usernameInput, { target: { value: 'testuser' } });
  fireEvent.change(passwordInput, { target: { value: 'ValidPassword1' } });

  // Check if the login button is rendered
  const loginButton = screen.getByRole('button', { name: /log in/i });
  expect(loginButton).toBeInTheDocument();

  // Simulate click on login button
  fireEvent.click(loginButton);
});