import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Signup from './signup';
import { BrowserRouter } from 'react-router-dom';

test('renders Signup component, checks validation, and submits form', async () => {
  render(
    <BrowserRouter>
      <Signup />
    </BrowserRouter>
  );

  const usernameInput = screen.getByAltText('username');
  const emailInput = screen.getByAltText('email');
  const passwordInput = screen.getByAltText('password');
  const password2Input = screen.getByAltText('password2');
  const apiKeyInput = screen.getByAltText('api_key');
  const ageInput = screen.getByAltText('age');
  const fullnameInput = screen.getByAltText('fullname');
  const signupButton = screen.getByRole('button', { name: /sign up/i });

  expect(usernameInput).toBeInTheDocument();
  expect(emailInput).toBeInTheDocument();
  expect(passwordInput).toBeInTheDocument();
  expect(password2Input).toBeInTheDocument();
  expect(apiKeyInput).toBeInTheDocument();
  expect(ageInput).toBeInTheDocument();
  expect(fullnameInput).toBeInTheDocument();
  expect(signupButton).toBeInTheDocument();

  fireEvent.change(usernameInput, { target: { value: 'usr' } });
  fireEvent.blur(usernameInput);
  expect(await screen.findByText(/Username must be 5-15 characters long/i)).toBeInTheDocument();

  fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
  fireEvent.blur(emailInput);
  expect(await screen.findByText(/Please enter a valid email address/i)).toBeInTheDocument();

  fireEvent.change(fullnameInput, { target: { value: 'A' } });
  fireEvent.blur(fullnameInput);
  expect(await screen.findByText(/Full name can only have letters/i)).toBeInTheDocument();

  fireEvent.change(ageInput, { target: { value: '150' } });
  fireEvent.blur(ageInput);
  expect(await screen.findByText(/Age must be a number between 0 and 120/i)).toBeInTheDocument();

  fireEvent.change(passwordInput, { target: { value: 'short' } });
  fireEvent.blur(passwordInput);
  expect(await screen.findByText(/Password must be 7-25 characters/i)).toBeInTheDocument();

  fireEvent.change(password2Input, { target: { value: 'differentpassword' } });
  fireEvent.blur(password2Input);
  expect(await screen.findByText(/Passwords do not match/i)).toBeInTheDocument();

  // 3. Clear errors with valid inputs
  fireEvent.change(usernameInput, { target: { value: 'validusername' } });
  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.change(fullnameInput, { target: { value: 'John Doe' } });
  fireEvent.change(ageInput, { target: { value: '25' } });
  fireEvent.change(passwordInput, { target: { value: 'ValidPass123' } });
  fireEvent.change(password2Input, { target: { value: 'ValidPass123' } });

  await waitFor(() => {
    expect(screen.queryByText(/Username must be 5-15 characters long/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Please enter a valid email address/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Full name can only have letters/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Age must be a number between 0 and 120/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Password must be 7-25 characters/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Passwords do not match/i)).not.toBeInTheDocument();
  });

  fireEvent.click(signupButton);
});