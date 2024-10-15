import React, { useState, useEffect } from 'react';
import board from './assets/board.png';
import './app.css';
import ruler from './assets/ruler.png';
import pencil from './assets/pencil.png';  // Import the pencil icon
import edit from './assets/penciledit.png';
import SideTab from './sidetab';
import { useNavigate } from 'react-router-dom';
import CryptoJS from 'crypto-js';

const secretKey = 'YX9YLwraTdKLCvmLauhs100EGaSiTF+r0SdYz1jx1oY=';
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

const encryptData = (data, secretKey) => {
    const key = CryptoJS.enc.Base64.parse(secretKey);  // Use a Base64 key
    const iv = CryptoJS.lib.WordArray.random(16);  // Generate random 16-byte IV

    const encrypted = CryptoJS.AES.encrypt(data, key, {
        iv: iv,
        padding: CryptoJS.pad.Pkcs7,
        mode: CryptoJS.mode.CBC
    });

    return {
        ciphertext: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
        iv: iv.toString(CryptoJS.enc.Base64)  // Send the IV along with the encrypted data
    };
};

function Settings() {
    const api_url = process.env.REACT_APP_API_URL;
    const [username, set_username] = useState('');
    const [account_type, set_account_type] = useState('');
    const [email, set_email] = useState('');
    const [password, set_password] = useState('PLACEHOLDER');
    const [password2, set_password2] = useState('PLACEHOLDER');
    const [api_key, set_api_key] = useState('PLACEHOLDER');
    const [age, set_age] = useState('');
    const [fullname, set_fullname] = useState('');
    const [error, set_error] = useState({});
    const [is_loading, set_is_loading] = useState(false);
    const [is_editing, set_is_editing] = useState('');  // Track which field is being edited
    const navigate = useNavigate();

    const fetch_user_data = async () => {
        try {
            const response = await fetch(`${api_url}/get_user/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': get_cookie('csrftoken'),
                },
                credentials: 'include',
            });

            const data = await response.json();

            if (response.ok) {
                // Populate the state with fetched user data
                set_username(data.username);
                set_account_type(data.account_type);
                set_email(data.email);
                set_api_key('PLACEHOLDER');  // Placeholder for security
                set_password('PLACEHOLDER'); // Placeholder for security
                set_password2('PLACEHOLDER');
                set_age(data.age);
                set_fullname(data.full_name);
            } else {
                console.error('Error fetching user data:', data.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    useEffect(() => {
        // Fetch user data when component mounts
        fetch_user_data();
    }, [api_url]);

    const handle_change = (setter, validate_fn) => (event) => {
        setter(event.target.value);
        if (validate_fn) validate_fn(event.target.value);
    };

    const handle_edit = (field) => {
        set_is_editing(field);
        if (field === 'password') {
            set_password('');
            set_password2('');
        }
        if (field === 'api_key') {
            set_api_key('');
        }
    };

    const handle_cancel = () => {
        set_error({});
        set_password('PLACEHOLDER');
        set_api_key('PLACEHOLDER');
        set_is_editing('');
        fetch_user_data();  // Reset the fields
    };

    const handle_submit = async (event, field) => {
        event.preventDefault();
        set_is_loading(true);

        try {
            const form_data = new URLSearchParams();
            // Encrypt sensitive fields before submission
            if (field === 'password' || field === 'api_key') {
                const encrypted_field = encryptData(eval(field), secretKey);  // Encrypt the data
                form_data.append(field, JSON.stringify(encrypted_field));  // Convert to JSON and send
            } else {
                form_data.append(field, eval(field));  // Dynamically assign the field to update
            }

            const response = await fetch(`${api_url}/update_account/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': get_cookie('csrftoken'),
                },
                credentials: 'include',
                body: form_data.toString(),
            });

            const data = await response.json();

            if (response.ok) {
                set_is_editing('');
                if (field === 'email') {
                    navigate('/verifyemail/' + username);
                }
            }
            set_error(data.errors || { submit: data.message });
        } catch (error) {
            console.error('Error:', error);
            set_error(prev => ({ ...prev, submit: 'An error occurred during submission. Please try again.' }));
        } finally {
            set_is_loading(false);
        }
    };

    const is_valid_username = (value) => {
        const username_pattern = /^[A-Za-z0-9_.-]{5,15}$/;
        if (!username_pattern.test(value)) {
            set_error(prev => ({ ...prev, username: 'Username must be 5-15 characters long and can only contain letters, numbers, (_), (-), and (.).' }));
            return false;
        }
        set_error(prev => ({ ...prev, username: '' }));
        return true;
    };

    const is_valid_email = (value) => {
        const email_pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email_pattern.test(value)) {
            set_error(prev => ({ ...prev, email: 'Please enter a valid email address.' }));
            return false;
        }
        set_error(prev => ({ ...prev, email: '' }));
        return true;
    };

    const is_valid_password = (value) => {
        const password_pattern = /^(?=.*[A-Z])(?=.*\d).{7,25}$/;
        if (!password_pattern.test(value)) {
            set_error(prev => ({ ...prev, password: 'Password must be 7-25 characters long, with at least one uppercase letter and one number.' }));
            return false;
        }
        set_error(prev => ({ ...prev, password: '' }));
        return true;
    };

    const validate_passwords = (value) => {
        if (value !== password) {
            set_error(prev => ({ ...prev, password2: 'Passwords do not match.' }));
            return false;
        }
        set_error(prev => ({ ...prev, password2: '' }));
        return true;
    };

    const is_field_locked = (field) => {
        if (is_editing === 'password' && (field === 'password' || field === 'password2')) {
            return false;  // Both 'password' and 'password2' should be unlocked if 'password' is being edited
        }
        return is_editing !== field;
    };
    

    return (
        <div className="App">
            <header className="App-header">
                <SideTab user="username" />
                <img src={board} className="App-board" draggable="false" />
                <img src={ruler} className="App-ruler" draggable="false" />
                <img src={pencil} className="App-pencil" draggable="false" />

                <div className="App-container">
                    <div className="App-SignupForm">
                        <div className="App-FormName">
                            <h4>settings</h4>
                        </div>
                        <form>
                            {/* Username */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>username</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('username')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={username}
                                        placeholder=""
                                        onChange={handle_change(set_username, is_valid_username)}
                                        disabled={is_field_locked('username')}
                                    />
                                </div>
                                {is_editing === 'username' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'username')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                                {error.username && <p className='Form-Error'>{error.username}</p>}
                            </div>

                            {/* Account Type */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>account type</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('account_type')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <select
                                        className="Signup-AccountTypeSelect"
                                        value={account_type}
                                        onChange={handle_change(set_account_type)}
                                        disabled={is_field_locked('account_type')}
                                    >
                                        <option value="1">player</option>
                                        <option value="2">researcher</option>
                                    </select>
                                </div>
                                {is_editing === 'account_type' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'account_type')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                            </div>

                            {/* Email */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>email</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('email')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={email}
                                        placeholder=""
                                        onChange={handle_change(set_email, is_valid_email)}
                                        disabled={is_field_locked('email')}
                                    />
                                </div>
                                {is_editing === 'email' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'email')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                                {error.email && <p className='Form-Error'>{error.email}</p>}
                            </div>

                            {/* Password */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>password</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('password')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="password"
                                        value={password}
                                        placeholder="enter new password"
                                        onChange={handle_change(set_password, is_valid_password)}
                                        disabled={is_field_locked('password')}
                                    />
                                </div>
                                {is_editing === 'password' && (
                                    <div>
                                        <div className="App-Rectangle" style={{ marginTop: '1rem' }}>
                                            <input
                                                type="password"
                                                value={password2}
                                                placeholder="re-enter new password"
                                                onChange={handle_change(set_password2, validate_passwords)}
                                            />
                                        </div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'password')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                                {error.password && <p className='Form-Error'>{error.password}</p>}
                                {error.password2 && <p className='Form-Error'>{error.password2}</p>}
                            </div>

                            {/* API Key */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>api key</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('api_key')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="password"
                                        value={api_key}
                                        placeholder="enter new api key"
                                        onChange={handle_change(set_api_key)}
                                        disabled={is_field_locked('api_key')}
                                    />
                                </div>
                                {is_editing === 'api_key' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'api_key')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                            </div>

                            {/* Age */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>age</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('age')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="number"
                                        value={age}
                                        placeholder=""
                                        onChange={handle_change(set_age)}
                                        disabled={is_field_locked('age')}
                                    />
                                </div>
                                {is_editing === 'age' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'age')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                                {error.age && <p className='Form-Error'>{error.age}</p>}
                            </div>

                            {/* Full Name */}
                            <div className="Signup-Query">
                                <div className="App-NormalText edit-container">
                                    <p>full name</p>
                                    <img
                                        src={edit}
                                        className="edit-icon"
                                        alt="edit"
                                        onClick={() => handle_edit('fullname')}
                                    />
                                </div>
                                <div className="App-Rectangle">
                                    <input
                                        type="text"
                                        value={fullname}
                                        placeholder=""
                                        onChange={handle_change(set_fullname)}
                                        disabled={is_field_locked('fullname')}
                                    />
                                </div>
                                {is_editing === 'fullname' && (
                                    <div>
                                        <button className='Small-Button' onClick={(e) => handle_submit(e, 'fullname')}>submit</button>
                                        <button className='Small-Button' onClick={handle_cancel}>cancel</button>
                                    </div>
                                )}
                                {error.fullname && <p className='Form-Error'>{error.fullname}</p>}
                            </div>

                            {error.submit && <p className='Form-Error'>{error.submit}</p>}
                        </form>
                    </div>
                </div>
            </header>
        </div>
    );
}

export default Settings;
