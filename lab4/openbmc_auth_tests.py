import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BMC_IP = "localhost"
BMC_PORT = "2443"
LOGIN_URL = f"https://{BMC_IP}:{BMC_PORT}/login"
USERNAME = "root"
PASSWORD = "0penBmc"
INVALID_PASSWORD = "invalid"

@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Safari()
    driver.maximize_window()

    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)

    try:
        driver.find_element(By.ID, "details-button").click()
        driver.find_element(By.ID, "proceed-link").click()
    except:
        pass
    return driver


def test_successful_auth(driver):
    """Тест успешной авторизации."""
    driver.find_element(By.XPATH, "//input[@id='username']").send_keys(USERNAME)
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@data-test-id='login-button-submit']").click()
    
def test_invalid_credentials(driver):
    """Тест неверных данных."""
    driver.find_element(By.XPATH, "//input[@id='username']").send_keys(USERNAME)
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(INVALID_PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
def test_multiple_auth(driver):
    """Тест блокировки"""
    for _ in range(5):
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='username']"))
        ).send_keys(USERNAME)
    
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(INVALID_PASSWORD)
    driver.find_element(By.XPATH, "//button[@data-test-id='login-button-submit']").click()
    
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading-indicator')]"))
    )

if __name__ == "__main__":
    pytest.main(["-v", "openbmc_auth_tests.py"])
