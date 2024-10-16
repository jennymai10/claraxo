import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="function")
def driver():
    """
    This fixture sets up and tears down the WebDriver instance for each test.
    """
    service = Service("/Users/jennymai/chromedriver-mac-x64/chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    yield driver
    driver.quit()


def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present on the page.
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def test_signup(driver):
    # Open the signup page
    driver.get("http://localhost:3000/signup")
    time.sleep(3)  # Let the page fully load

    # Test invalid username
    username_input = wait_for_element(driver, By.ID, 'signup_username')
    username_input.clear()
    username_input.send_keys("in")  # Invalid, too short
    username_input.send_keys("\t")  # Trigger validation
    time.sleep(2)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Username must be 5-15 characters" in error_message

    # Test valid username
    username_input.clear()
    username_input.send_keys("validusername")
    time.sleep(2)

    account_type_input = wait_for_element(driver, By.ID, 'signup_account_type')
    account_type_input.click()
    account_type_input.send_keys("player")  # Select the first option
    time.sleep(2)

    # Test invalid email
    email_input = wait_for_element(driver, By.ID, 'signup_email')
    email_input.clear()
    email_input.send_keys("invalid-email")  # Invalid email format
    email_input.send_keys("\t")  # Trigger validation
    time.sleep(2)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Please enter a valid email address" in error_message

    # Test valid email
    email_input.clear()
    email_input.send_keys("validemail@example.com")
    time.sleep(2)

    # Test weak password
    password_input = wait_for_element(driver, By.ID, 'signup_password')
    password_input.clear()
    password_input.send_keys("weak")  # Weak password
    password_input.send_keys("\t")  # Trigger validation
    time.sleep(2)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Password must be 7-25 characters" in error_message

    # Test valid password
    password_input.clear()
    password_input.send_keys("ValidPassword123")
    time.sleep(2)

    # Test password mismatch
    password2_input = wait_for_element(driver, By.ID, 'signup_password2')
    password2_input.clear()
    password2_input.send_keys("DifferentPassword123")  # Mismatch
    password2_input.send_keys("\t")  # Trigger validation
    time.sleep(2)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Passwords do not match" in error_message

    # Test matching password
    password2_input.clear()
    password2_input.send_keys("ValidPassword123")
    time.sleep(2)

    # Test valid API key
    api_key_input = wait_for_element(driver, By.ID, 'signup_api_key')
    api_key_input.clear()
    api_key_input.send_keys("ValidAPIKey123")
    time.sleep(2)

    # Test valid age
    age_input = wait_for_element(driver, By.ID, 'signup_age')
    age_input.clear()
    age_input.send_keys("25")
    time.sleep(2)

    # Test valid full name
    fullname_input = wait_for_element(driver, By.ID, 'signup_fullname')
    fullname_input.clear()
    fullname_input.send_keys("John Doe")
    time.sleep(2)

    # Submit the form
    signup_button = wait_for_element(driver, By.CSS_SELECTOR, '.App-Button')
    signup_button.click()

    time.sleep(20)  # Wait for the submission to process

    # Check if redirected to the verify email page
    assert "verifyemail" in driver.current_url

def test_resend_email(driver):
    # Open the Verify Email page
    driver.get("http://localhost:3000/verifyemail")
    time.sleep(3)

    # Simulate resending the verification email
    resend_link = wait_for_element(driver, By.ID, "resend_link")
    resend_link.click()
    time.sleep(1)

    # Enter the username for the resend
    resend_username_input = wait_for_element(driver, By.ID, 'resend_username')
    resend_username_input.clear()
    resend_username_input.send_keys("validusername")
    time.sleep(2)

    # Click the 'resend email' button
    resend_button = wait_for_element(driver, By.CSS_SELECTOR, '.App-Button')
    resend_button.click()
    time.sleep(7)

    # Check for a success message
    resend_success_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Message').text
    assert "Verification email resent successfully!" in resend_success_message

def test_verify_email(driver):
    # Open the Verify Email page
    driver.get("http://localhost:3000/verifyemail")
    time.sleep(3)  # Let the page fully load

    # Enter valid username
    username = "validusername"  # Replace with the actual username you want to test
    username_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="text"]')
    username_input.clear()
    username_input.send_keys(username)
    time.sleep(1)

    # Test invalid verification code (e.g., less than 6 digits)
    verification_code_input = wait_for_element(driver, By.ID, 'verification_code')
    verification_code_input.clear()
    verification_code_input.send_keys("123")
    verification_code_input.send_keys("\t")  # Trigger validation
    time.sleep(1)

    # Verify error message for invalid code
    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Invalid Verification Code. Must be 6 digits." in error_message

    # Test valid verification code from the database
    verification_code_input.clear()
    time.sleep(20)

    # Submit the form with the valid code
    verify_button = wait_for_element(driver, By.CSS_SELECTOR, '.App-Button')
    verify_button.click()
    time.sleep(3)

    # Check if redirected to the success page or if there is a verification message
    assert driver.current_url != "http://localhost:3000/verifyemail"

def test_login(driver):
    # Open the login page
    driver.get("http://localhost:3000/login")
    time.sleep(3)  # Let the page fully load

    # Test invalid username (less than 5 characters)
    username_input = wait_for_element(driver, By.ID, 'username')
    username_input.clear()
    username_input.send_keys("usr")
    username_input.send_keys("\t")  # Trigger validation
    login_button = wait_for_element(driver, By.ID, 'login_button')
    login_button.click()
    time.sleep(2)

    # Verify the error message for invalid username
    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Username must be 5-15 characters" in error_message

    # Test valid username
    username_input.clear()
    username_input.send_keys("validusername")
    time.sleep(1)

    # Test weak password (less than 7 characters)
    password_input = wait_for_element(driver, By.ID, 'password')
    password_input.clear()
    password_input.send_keys("weak")
    login_button.click()
    time.sleep(3)

    # Verify the error message for invalid password
    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Password must be 7-25 characters" in error_message

    # Test valid password
    password_input.clear()
    password_input.send_keys("ValidPassword123")
    time.sleep(1)

    # Click the login button
    login_button.click()
    time.sleep(10)  # Wait for login to complete

    # Check if redirected to the success page or dashboard
    assert "game" in driver.current_url  # Adjust depending on actual URL


def test_signup_redirect(driver):
    # Open the login page
    driver.get("http://localhost:3000/login")
    time.sleep(3)

    # Click the signup button to redirect to the signup page
    signup_button = wait_for_element(driver, By.ID, 'signup_button')
    signup_button.click()
    time.sleep(3)

    # Check if redirected to the signup page
    assert "signup" in driver.current_url