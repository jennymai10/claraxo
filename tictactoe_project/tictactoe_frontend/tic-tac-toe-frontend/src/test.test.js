import { render } from '@testing-library/react';
import Login from './login';
import { BrowserRouter } from 'react-router-dom'; // Wrap with Router if the component uses routing

test('renders Login component', () => {
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
});
