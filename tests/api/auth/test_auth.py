import pytest
from framework.api.core.logger import logger
from framework.api.resources.auth.auth_exceptions import AuthenticationError


# Авторизация с валидацией полей. получаем response из текущей сессии.
# @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
# def test_auth(base_url, framework_context):
#     auth_tool = framework_context.tools_manager.auth
#     response = auth_tool.get_current_session()
#
#     logger.info(f"Login Response Data: {response}")
#     logger.info(f"User Role: {response['data']['role']}")
#
#     # Verify login success
#     assert response["sid"] is not None
#     assert response["data"]["login"] == "admin"
#     assert response["data"]["role"] == "admin"
#     assert response["data"]["remember"] is True
#     assert "jwtAccessExpirationDate" in response
#     assert "jwtRefreshExpirationDate" in response
#
#     # Verify cookies are set
#     cookies = auth_tool.cookie_manager.get_current_cookies()
#     logger.info(f"Cookies after login: {cookies}")
#     assert "BAUMSID" in cookies
#     assert "jwt_access" in cookies
#     assert "jwt_refresh" in cookies
#
#     # Perform logout
#     logout_response = auth_tool.logout()
#     assert logout_response.status_code in (200, 204)

# Авторизация с валидацией полей. получаем response из прямого запроса на аутентификацию.

@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
def test_auth(base_url, framework_context):
    auth_tool = framework_context.tools_manager.auth
    # response = auth_tool.authentication()
    response = auth_tool.get_current_session()

    logger.info(f"Login Response Data: {response}")
    logger.info(f"User Role: {response['data']['role']}")

    # Verify login success
    assert response["sid"] is not None
    assert response["data"]["login"] == "admin"
    assert response["data"]["role"] == "admin"
    assert response["data"]["remember"] is True
    assert "jwtAccessExpirationDate" in response
    assert "jwtRefreshExpirationDate" in response

    # Verify cookies are set
    cookies = auth_tool.cookie_manager.get_current_cookies()
    logger.info(f"Cookies after login: {cookies}")
    assert "BAUMSID" in cookies
    assert "jwt_access" in cookies
    assert "jwt_refresh" in cookies

    # Perform logout
    logout_response = auth_tool.logout()
    assert logout_response["success"] is True
    assert logout_response["status_code"] in (200, 204)


# Login\logout на разных нодах
@pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
def test_cross_node_scenario(framework_context, node_switcher):
    response = framework_context.tools_manager.auth.get_current_session()
    auth_tool = framework_context.tools_manager.auth
    # Логин на NODE_1
    node_switcher("NODE_1")
    assert response["sid"] is not None

    # Логаут на NODE_2
    node_switcher("NODE_2")
    logout_response = auth_tool.logout()
    assert logout_response["status_code"] == 500

    # Логаут на NODE_1
    node_switcher("NODE_1")
    logout_response = auth_tool.logout()
    auth_tool.clean_session_data()
    assert logout_response["status_code"] in (200, 204)



# Test with credentials
@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
@pytest.mark.parametrize("framework_context", [{
    "credentials": {
        "username": "admin",
        "password": "123456",
        "remember": True
    },
}], indirect=True)
def test_custom_auth(framework_context):
    response = framework_context.tools_manager.auth.get_current_session()
    assert response["data"]["login"] == "admin"


# Test with forced authentication
@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
def test_force_auth(framework_context):
    response = framework_context.tools_manager.auth.force_authentication().json()
    logger.info(f"I call auth in test")
    assert response["sid"] is not None
    assert response["data"]["login"] == "admin"


# @pytest.mark.auth_scope("session")

# Тест с ручным добавление кредов авторизации
@pytest.mark.auth_scope("function")
@pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
@pytest.mark.parametrize("framework_context", [
    {"credentials": creds} for creds in [
        {"username": "admin", "password": "123456", "remember": True},
        {"username": "user", "password": "123456", "remember": True},
        {"username": "admin", "password": "123456", "remember": False}
    ]
], indirect=True)
def test_different_user_auth(framework_context):
    auth_tool = framework_context.tools_manager.auth
    # Perform login
    # response = auth_tool.authentication()
    # response = auth_tool.get_current_session()

    # Verify login success
    # assert response["sid"] is not None

    # Perform logout
    # auth_tool.logout_and_clean()


@pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
def test_invalid_credentials(framework_context):
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        framework_context.tools_manager.auth.configure(
            username="admin",
            password="123456",
            remember=True
        )
        framework_context.tools_manager.auth.login()



#
#
# @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
# @pytest.mark.parametrize("credentials", [
#     {"username": "admin", "password": "123456"},
# ])
# def test_token_refresh_mechanism(configured_auth):
#     auth_tool = configured_auth.tools_manager.auth
#
#     # 1. Initial login and cookie capture
#     auth_tool.login()
#     initial_cookies = auth_tool.cookie_manager.get_current_cookies()
#     # logger.info("\n=== Initial Cookies ===")
#     # for cookie_name, cookie_value in initial_cookies.items():
#     #     logger.info(f"{cookie_name}: {cookie_value}")
#
#     # 2. Verify initial access
#
#     # 3. Wait for token expiration
#     logger.info("Waiting 185sec for token expiration...")
#     time.sleep(185)
#
#     # 4. Verify expired token behavior
#
#     # 5. Refresh tokens and compare cookies
#     # auth_tool.refresh_tokens()
#     new_cookies = auth_tool.cookie_manager.get_current_cookies()
#
#     # logger.info("\n=== Cookie Comparison ===")
#     # logger.info("Old Cookies:")
#     # for cookie_name, cookie_value in initial_cookies.items():
#     #     logger.info(f"{cookie_name}: {cookie_value}")
#     #
#     # logger.info("\nNew Cookies:")
#     # for cookie_name, cookie_value in new_cookies.items():
#     #     logger.info(f"{cookie_name}: {cookie_value}")
#
#     # Verify cookies have changed
#     for cookie_name in ['jwt_access', 'jwt_refresh']:
#         assert initial_cookies.get(cookie_name) != new_cookies.get(cookie_name), \
#             f"Cookie {cookie_name} should be different after refresh"
#
#     # 6. Verify renewed access
#
#     # Cleanup
#     auth_tool.logout()
#
#
