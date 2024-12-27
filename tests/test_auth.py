import pytest
from framework.logger import logger


@pytest.fixture
def configured_auth(framework_context, credentials):
    """Fixture configures auth with specific credentials"""
    framework_context.tools_manager.auth.configure(
        username=credentials["username"],
        password=credentials["password"]
    )
    return framework_context


@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
@pytest.mark.parametrize("keys_to_extract", [["name"]])
@pytest.mark.parametrize("credentials", [
    {"username": "admin", "password": "123456"},
    # {"username": "user", "password": "user_pass"},
    # {"username": "readonly", "password": "readonly_pass"}
])
def test_different_user_auth(configured_auth):

    # Perform login
    login_response = configured_auth.tools_manager.auth.login()
    response = login_response.json()
    logger.info(f"Login response: {response}\n Headers: {login_response}")


    # Verify login success
    assert response["sid"] is not None

    # Perform logout
    configured_auth.tools_manager.auth.logout()


@pytest.mark.parametrize("login_data", [
    {"username": "admin", "password": "admin_pass"},
])
def test_pool_creation(framework_context, login_data):
    # Login with parametrized data
    framework_context.tools_manager.auth.login(login_data)

    # Create pool using pool tools
    pool_config = {...}
    result = framework_context.tools_manager.pool.create_pool(pool_config)

    # Assertions
    assert result["status"] == "success"

    # Cleanup
    framework_context.tools_manager.auth.logout()

