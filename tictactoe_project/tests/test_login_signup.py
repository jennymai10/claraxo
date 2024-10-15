import pytest, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    driver.get("http://localhost:3000/signup")
    time.sleep(3)
    
    # Enter an invalid username
    username_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="text"]')
    username_input.send_keys("in")  # too short username
    username_input.send_keys(Keys.TAB)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Username must be 5-15 characters" in error_message

    # Test valid username
    username_input.clear()
    username_input.send_keys("validusername")

    # Test invalid email
    email_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="text"][value=""]')
    email_input.clear()
    email_input.send_keys("invalid-email")  # Invalid email format
    email_input.send_keys(Keys.TAB)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Please enter a valid email address" in error_message

    # Test valid email
    email_input.clear()
    email_input.send_keys("validemail@example.com")

    # Test weak password
    password_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="password"]')
    password_input.clear()
    password_input.send_keys("weak")  # Password doesn't meet requirements
    password_input.send_keys(Keys.TAB)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Password must be 7-25 characters" in error_message

    # Test valid password
    password_input.clear()
    password_input.send_keys("ValidPassword123")

    # Update: Use a different, more specific selector for "re-enter password"
    password2_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="password"]:nth-of-type(2)')  # Using nth-of-type

    # Test password confirmation mismatch
    password2_input.clear()
    password2_input.send_keys("DifferentPassword123")
    password2_input.send_keys(Keys.TAB)

    error_message = wait_for_element(driver, By.CSS_SELECTOR, '.Form-Error').text
    assert "Passwords do not match" in error_message

    # Test matching password confirmation
    password2_input.clear()
    password2_input.send_keys("ValidPassword123")

    # Test API key input
    api_key_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="password"][placeholder="enter new api key"]')
    api_key_input.clear()
    api_key_input.send_keys("ValidAPIKey123")

    # Test valid age
    age_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="number"]')
    age_input.clear()
    age_input.send_keys("25")

    # Test full name
    fullname_input = wait_for_element(driver, By.CSS_SELECTOR, 'input[type="text"][placeholder=""]')
    fullname_input.clear()
    fullname_input.send_keys("John Doe")

    # Submit the signup form
    signup_button = wait_for_element(driver, By.CSS_SELECTOR, '.App-Button')
    signup_button.click()

    time.sleep(3)  # Wait for the submission to process

    # Check if the user is redirected to the verification page
    assert "verifyemail" in driver.current_url