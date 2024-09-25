from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_login():
    driver = webdriver.Chrome()  # Initialize the WebDriver (make sure to point it to the right path)
    driver.get("http://localhost:3000/login")  # Visit the login page

    # Test if the username field accepts valid input
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    username_input.send_keys("validuser")

    # Test if the password field accepts valid input
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.send_keys("ValidPassword123")

    # Click the login button
    login_button = driver.find_element(By.CSS_SELECTOR, '.App-Button')
    login_button.click()

    time.sleep(2)  # Wait for the login to process

    # Check if the user is redirected to the correct page
    assert "new_game" in driver.current_url

    driver.quit()

test_login()

def test_signup():
    driver = webdriver.Chrome()  # Initialize the WebDriver
    driver.get("http://localhost:3000/signup")  # Visit the signup page

    # Test username validation (invalid username)
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    username_input.send_keys("in")  # Enter invalid username (too short)
    username_input.send_keys(Keys.TAB)

    error_message = driver.find_element(By.CSS_SELECTOR, '.Form-Error').text
    assert "Username must be 5-15 characters" in error_message

    # Clear input and enter valid username
    username_input.clear()
    username_input.send_keys("validusername")

    # Test if email field validates correct email format
    email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][placeholder=""]')
    email_input.send_keys("invalid-email")
    email_input.send_keys(Keys.TAB)

    error_message = driver.find_element(By.CSS_SELECTOR, '.Form-Error').text
    assert "Please enter a valid email address" in error_message

    # Test password validation (invalid password)
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.send_keys("weak")  # Enter weak password
    password_input.send_keys(Keys.TAB)

    error_message = driver.find_element(By.CSS_SELECTOR, '.Form-Error').text
    assert "Password must be 7-25 characters" in error_message

    # Enter valid password and re-enter password
    password_input.clear()
    password_input.send_keys("ValidPassword123")
    password2_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"][placeholder="re-enter password"]')
    password2_input.send_keys("ValidPassword123")

    # Submit the signup form
    signup_button = driver.find_element(By.CSS_SELECTOR, '.App-Button')
    signup_button.click()

    time.sleep(2)  # Wait for the signup process

    # Check if the user is redirected to the verification page
    assert "verifyemail" in driver.current_url

    driver.quit()

test_signup()

def test_verify_email():
    driver = webdriver.Chrome()  # Initialize the WebDriver
    driver.get("http://localhost:3000/verifyemail/validuser")  # Visit the verification page

    # Enter an invalid verification code (less than 6 digits)
    verification_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][placeholder=""]')
    verification_input.send_keys("123")  # Invalid code
    verification_input.send_keys(Keys.TAB)

    error_message = driver.find_element(By.CSS_SELECTOR, '.Form-Error').text
    assert "Invalid Verification Code" in error_message

    # Clear input and enter valid code
    verification_input.clear()
    verification_input.send_keys("123456")  # Valid code

    # Click verify button
    verify_button = driver.find_element(By.CSS_SELECTOR, '.App-Button')
    verify_button.click()

    time.sleep(2)  # Wait for the verification process

    # Check if the user is redirected to the new game page
    assert "new_game" in driver.current_url

    driver.quit()

test_verify_email()

def test_invalid_login():
    driver = webdriver.Chrome()  # Initialize the WebDriver
    driver.get("http://localhost:3000/login")  # Visit the login page

    # Test invalid login
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    username_input.send_keys("wronguser")

    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.send_keys("WrongPassword123")

    login_button = driver.find_element(By.CSS_SELECTOR, '.App-Button')
    login_button.click()

    time.sleep(2)  # Wait for the response

    # Check for error message
    error_message = driver.find_element(By.CSS_SELECTOR, '.Form-Error').text
    assert "Incorrect username or password" in error_message

    driver.quit()

test_invalid_login()