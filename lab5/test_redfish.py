import pytest
import requests
import time
import logging
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("openbmc_tests.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BMC_IP = "localhost"
BMC_PORT = 2443
BASE_URL = f"https://{BMC_IP}:{BMC_PORT}"
REDFISH_BASE = f"{BASE_URL}/redfish/v1"
USERNAME = "root"
PASSWORD = "0penBmc"
SSL_VERIFY = False

@pytest.fixture(scope="session")
def auth_token() -> str:
    """Фикстура для получения токена аутентификации"""
    logger.info("Инициализация аутентификационного токена...")
    url = f"{REDFISH_BASE}/SessionService/Sessions"
    try:
        response = requests.post(
            url,
            json={"UserName": USERNAME, "Password": PASSWORD},
            headers={"Content-Type": "application/json"},
            verify=SSL_VERIFY
        )
        response.raise_for_status()
        token = response.headers["X-Auth-Token"]
        logger.info("Токен успешно получен")
        return token
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        pytest.fail("Не удалось получить токен аутентификации")

def test_auth_openbmc(auth_token: str):
    """Тест аутентификации в OpenBMC"""
    logger.info("Запуск теста аутентификации...")
    
    url = f"{REDFISH_BASE}/SessionService/Sessions"
    response = requests.post(
        url,
        json={"UserName": USERNAME, "Password": PASSWORD},
        headers={"Content-Type": "application/json"},
        verify=SSL_VERIFY
    )
    
    try:
        assert response.status_code == 201, "Неверный статус-код ответа"
        assert "X-Auth-Token" in response.headers, "Токен отсутствует в заголовках"
        logger.info("Аутентификация прошла успешно")
    except AssertionError as ae:
        logger.error(f"Тест аутентификации не пройден: {str(ae)}")
        pytest.fail(str(ae))

def test_power_management(auth_token: str):
    """Тест управления питанием системы"""
    logger.info("Запуск теста управления питанием...")
    
    headers = {
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json"
    }
    power_url = f"{REDFISH_BASE}/Systems/system/Actions/ComputerSystem.Reset"
    system_url = f"{REDFISH_BASE}/Systems/system"
    
    try:
        logger.info(f"Используемый URL: {power_url}")
        logger.debug(f"Заголовки запроса: {headers}")
        
        logger.info("Отправка команды включения...")
        response = requests.post(
            power_url,
            json={"ResetType": "On"},
            headers=headers,
            verify=SSL_VERIFY
        )
        
        logger.info(f"Статус-код ответа: {response.status_code}")
        logger.debug(f"Полный ответ сервера: {response.text}")
        
        assert response.status_code == 204, (
            f"Ожидался статус 204, получен {response.status_code}. "
            f"Ответ сервера: {response.text}"
        )
         
    except requests.exceptions.HTTPError as he:
        logger.error(f"HTTP-ошибка: {he}\nОтвет сервера: {he.response.text}")
        pytest.fail("Ошибка выполнения запроса")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        pytest.fail("Необработанная ошибка в тесте")

if __name__ == "__main__":
    pytest.main(["-v", "-s", "--log-cli-level=INFO"])