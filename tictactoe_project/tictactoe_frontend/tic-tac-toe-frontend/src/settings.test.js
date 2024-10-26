import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Settings from './settings';
import { BrowserRouter } from 'react-router-dom';

test('renders Settings component, validates fields, and submits single field at a time', async () => {
    render(
      <BrowserRouter>
        <Settings />
      </BrowserRouter>
    );
    // Step 1: Test Username field
    fireEvent.click(screen.getByAltText('edit_button'));
    const usernameInput = screen.getByAltText('username');
    expect(usernameInput).toBeEnabled();

    fireEvent.change(usernameInput, { target: { value: 'usr' } });
    fireEvent.blur(usernameInput);
    expect(await screen.findByText(/Username must be 5-15 characters long/i)).toBeInTheDocument();

    fireEvent.change(usernameInput, { target: { value: 'validusername' } });
    await waitFor(() => expect(screen.queryByText(/Username must be 5-15 characters long/i)).not.toBeInTheDocument());

    fireEvent.click(screen.getByText('submit'));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    fireEvent.click(screen.getByText('cancel'));
    expect(usernameInput).toBeDisabled();
});