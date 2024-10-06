import React, { useState } from 'react';
import board from './assets/board.png';
import './app.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';
import { useNavigate, useParams } from 'react-router-dom';

/**
 * Retrieves the value of a specific cookie by its name.
 * 
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string|null} - Returns the value of the cookie if found, otherwise null.
 */
function get_cookie(name) {
    let cookie_value = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookie_value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookie_value;
}

/**
 * VerifyEmail component handles the email verification process.
 * It displays a form to input username and verification code, validates inputs, 
 * and makes an API call to verify the provided code.
 */
function VerifyEmail() {
    const params = useParams(); // Hook to access the route parameters.
    const [username, set_username] = useState(params.username || ''); // State to store the username, initialized with route param if available.
    const [verification_code, set_verification_code] = useState(''); // State to store the verification code input.
    const [error, set_error] = useState({}); // State to store error messages for the form.
    const navigate = useNavigate(); // React Router's hook for programmatic navigation.

        /**
     * Higher-order function that handles input changes and optionally validates the input.
     * 
     * @param {Function} setter - State setter function for updating the input value.
     * @param {Function} [validate_fn] - Optional validation function to validate input in real-time.
     * @returns {Function} - Returns an event handler function for input change.
     */
    const handle_change = (setter, validate_fn) => (event) => {
        setter(event.target.value);
        if (validate_fn) validate_fn(event.target.value);
    };

    /**
     * Validates the verification code format (6 digits only).
     * 
     * @param {string} value - The verification code input to validate.
     * @returns {boolean} - Returns true if the code is valid, otherwise false.
     */
    const is_valid_verification_code = (value) => {
        const code_pattern = /^\d{6}$/;
        if (!code_pattern.test(value)) {
            set_error(prev => ({ ...prev, verification_code: 'Invalid Verification Code. Must be 6 digits.' }));
            return false;
        }
        set_error(prev => ({ ...prev, verification_code: '' })); // Clear previous errors if the input is valid.
        return true;
    };

        /**
     * Handles the verify button click event.
     * Validates the verification code and sends a verification request to the server.
     * 
     * @param {Event} event - The click event triggered by the verify button.
     * @returns {void}
     */
    const handle_verify_click = async (event) => {
        event.preventDefault(); // Prevent the default form submission behavior.
        set_error({}); // Clear any previous error messages.

        // Validate the verification code input before making the verification request.
        if (is_valid_verification_code(verification_code)) {
            try {
                 // Prepare the form data for sending in the API request.
                const form_data = new URLSearchParams();
                form_data.append('username', username);
                form_data.append('verification_code', verification_code);

                // Send a POST request to the email verification API endpoint.
                const response = await fetch('http://localhost:8000/verifyemail/', {
                    method: 'POST', // HTTP method to use for the request.
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // Content type for form data submission.
                        'X-CSRFToken': get_cookie('csrftoken'), // CSRF token for security to protect against cross-site request forgery attacks.
                    },
                    credentials: 'include', // Include credentials such as cookies in the request.
                    body: form_data.toString(), // The form data to be sent in the request body.
                });

                // Parse the response as JSON.
                const data = await response.json();

                // Check if the response status is OK (status code 200-299).
                if (response.ok) {
                    // If the verification is successful, redirect the user to the provided URL.
                    if (data.status === 'success') {
                        navigate(data.redirect_url); // Redirect to the success page.
                    }
                } else {
                    console.log(data.errors);
                    // If the response contains errors, display them on the form.
                    if (data.errors) {
                        set_error(data.errors); // Display validation errors returned from the server.
                    } else {
                        set_error({ submit: data.message }); // Display a general error message if available.
                    }
                }
            } catch (error) {
                // Log any error that occurs during the request and set a general error message.
                console.error('Error:', error);
                set_error(prev => ({ ...prev, submit: 'An error occurred during verification. Please try again.' }));
            }
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <img src={board} className="App-board" draggable="false" />
                <img src={ruler} className="App-ruler" draggable="false" />
                <img src={pencil} className="App-pencil" draggable="false" />

                <div className="App-container">
                    <div className="App-SignupForm">
                        <div className="App-FormName">
                            <h4>verify email</h4>
                        </div>
                        <form>
                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>username</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={username}
                                        placeholder=""
                                        onChange={(e) => set_username(e.target.value)} 
                                    />
                                </div>
                            </div>

                            <div className="Signup-Query">
                                <div className="App-NormalText">
                                    <p>verification code</p>
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={verification_code}
                                        placeholder=""
                                        onChange={handle_change(set_verification_code, is_valid_verification_code)}
                                    />
                                </div>
                                {error.verification_code && <p className='Form-Error'>{error.verification_code}</p>}
                            </div>
                            {error.submit && <p className='Form-Error'>{error.submit}</p>}
                            <div className="App-Panel">
                                <button className="App-Button" onClick={handle_verify_click}>
                                    verify
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </header>
        </div>
    );
}

export default VerifyEmail;
