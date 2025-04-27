import pytest
import requests
import os
import logging
from typing import Dict, Any
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "openbmc_tests.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BMC_IP = os.getenv("BMC_HOST", "host.docker.internal")
BMC_PORT = os.getenv("BMC_PORT", "2443")
USERNAME = os.getenv("BMC_USER", "root")
PASSWORD = os.getenv("BMC_PASSWORD", "0penBmc")
SSL_VERIFY = os.getenv("SSL_VERIFY", "false").lower() == "true"

BASE_URL = f"https://{BMC_IP}:{BMC_PORT}"
REDFISH_BASE = f"{BASE_URL}/redfish/v1"

@pytest.fixture(scope="session")
def auth_token() -> str:
    """Фикстура для получения токена аутентификации с повторными попытками"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Попытка аутентификации {attempt}/{max_retries}...")
        try:
            response = requests.post(
                f"{REDFISH_BASE}/SessionService/Sessions",
                json={"UserName": USERNAME, "Password": PASSWORD},
                headers={"Content-Type": "application/json"},
                verify=SSL_VERIFY,
                timeout=10
            )
            response.raise_for_status()
            token = response.headers["X-Auth-Token"]
            logger.info("Токен успешно получен")
            return token
        except Exception as e:
            logger.warning(f"Ошибка аутентификации: {str(e)}")
            if attempt == max_retries:
                logger.error("Не удалось получить токен аутентификации")
                pytest.fail("Auth failed")
            time.sleep(retry_delay)

def test_redfish_service_availability():
    """Тест доступности Redfish Service"""
    logger.info("Проверка доступности Redfish Service...")
    try:
        response = requests.get(
            REDFISH_BASE,
            verify=SSL_VERIFY,
            timeout=10
        )
        assert response.status_code == 200, f"Некорректный статус: {response.status_code}"
        assert "RedfishVersion" in response.json(), "Отсутствует RedfishVersion в ответе"
        logger.info("Redfish Service доступен")
    except Exception as e:
        logger.error(f"Ошибка доступа к Redfish: {str(e)}")
        pytest.fail("Redfish Service недоступен")

def test_auth_openbmc(auth_token: str):
    """Тест аутентификации в OpenBMC"""
    logger.info("Запуск теста аутентификации...")
    
    try:
        response = requests.get(
            f"{REDFISH_BASE}/SessionService/Sessions",
            headers={"X-Auth-Token": auth_token},
            verify=SSL_VERIFY,
            timeout=10
        )
        response.raise_for_status()
        assert len(response.json()["Members"]) > 0, "Нет активных сессий"
        logger.info("Токен валиден, аутентификация подтверждена")
    except Exception as e:
        logger.error(f"Ошибка проверки токена: {str(e)}")
        pytest.fail("Token validation failed")

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
        status_response = requests.get(
            system_url,
            headers=headers,
            verify=SSL_VERIFY,
            timeout=10
        )
        status_response.raise_for_status()
        current_state = status_response.json()["PowerState"]
        logger.info(f"Текущее состояние питания: {current_state}")

        target_action = "On" if current_state != "On" else "ForceOff"
        logger.info(f"Отправка команды: {target_action}")

        response = requests.post(
            power_url,
            json={"ResetType": target_action},
            headers=headers,
            verify=SSL_VERIFY,
            timeout=30
        )
        
        assert response.status_code in [200, 204], (
            f"Неожиданный статус код: {response.status_code}. Ответ: {response.text}"
        )
        
        time.sleep(10)
        verify_response = requests.get(
            system_url,
            headers=headers,
            verify=SSL_VERIFY,
            timeout=10
        )
        new_state = verify_response.json()["PowerState"]
        assert new_state == ("On" if target_action == "On" else "Off"), (
            f"Состояние не изменилось как ожидалось. Текущее состояние: {new_state}"
        )
        
        logger.info(f"Успешное изменение состояния питания на {new_state}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка выполнения запроса: {str(e)}")
        pytest.fail("Power management test failed")
    except AssertionError as ae:
        logger.error(f"Проверка не пройдена: {str(ae)}")
        pytest.fail(str(ae))

if __name__ == "__main__":
    pytest.main([
        "-v", 
        "-s", 
        "--log-cli-level=INFO",
        "--bmc-host", os.getenv("BMC_HOST", "host.docker.internal"),
        "--bmc-port", os.getenv("BMC_PORT", "2443")
    ])