import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

BMC_IP = "localhost"
BMC_PORT = "2443"
LOGIN_URL = f"https://{BMC_IP}:{BMC_PORT}/login"
USERNAME = "root"
PASSWORD = "0penBmc"
INVALID_PASSWORD = "invalid"

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(LOGIN_URL)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "details-button"))
        ).click()
        driver.find_element(By.ID, "proceed-link").click()
    except:
        pass
    
    yield driver
    driver.quit()

def test_successful_auth(driver):
    """Тест успешной авторизации."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
    ).send_keys(USERNAME)
    
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@data-test-id='login-button-submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.url_changes(LOGIN_URL)
    )

def test_invalid_credentials(driver):
    """Тест неверных данных."""
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
    ).send_keys(USERNAME)
    
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(INVALID_PASSWORD)
    driver.find_element(By.XPATH, "//button[@data-test-id='login-button-submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Invalid credentials')]"))
    )

def test_multiple_auth(driver):
    """Тест блокировки после нескольких попыток."""
    driver.get(LOGIN_URL)
    for _ in range(5):
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
        ).send_keys(USERNAME)
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys(INVALID_PASSWORD)
        driver.find_element(By.XPATH, "//button[@data-test-id='login-button-submit']").click()
    
    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Too many failed attempts')]"))
    )
    assert "Too many failed attempts" in error_message.text

if __name__ == "__main__":
    pytest.main(["-v", "openbmc_auth_tests.py"])