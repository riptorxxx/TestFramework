import pytest
from framework.core.logger import logger


# @pytest.fixture
# def configured_auth(framework_context, credentials):
#     """Fixture configures auth with specific credentials"""
#     framework_context.tools_manager.auth.configure(
#         username=credentials["username"],
#         password=credentials["password"]
#     )
#     return framework_context

@pytest.fixture
def configured_auth_ctx(framework_context, request):
    """Fixture configures auth with credentials from params or env"""
    if hasattr(request, 'param'):
        framework_context.tools_manager.auth.configure(**request.param)
    else:
        framework_context.tools_manager.auth.configure()
    return framework_context


# Авторизация с валидацией полей.
@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
def test_auth(base_url, framework_context):
    auth_tool = framework_context.tools_manager.auth
    auth_tool.configure()

    # Perform login
    login_response = auth_tool.login()
    response = login_response.json()

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
    assert logout_response.status_code in (200, 204)



# Login\logout на разных нодах
def test_cross_node_scenario(framework_context, node_switcher):
    auth_tool = framework_context.tools_manager.auth

    # Логин на NODE_1
    node_switcher("NODE_1")
    framework_context.tools_manager.auth.configure()
    login_response = auth_tool.login()
    assert login_response.json()["sid"] is not None

    # Логаут на NODE_2
    node_switcher("NODE_2")
    logout_response = auth_tool.logout()
    assert logout_response.status_code in (200, 204)


# Тест с ручным добавление кредов авторизации
@pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
@pytest.mark.parametrize("configured_auth_ctx", [
    {"username": "admin", "password": "123456", "remember": True},
    # {"username": "user", "password": "user_pass"},
    # {"username": "readonly", "password": "readonly_pass"}
], indirect=True)
def test_different_user_auth(configured_auth_ctx):

    # Perform login
    login_response = configured_auth_ctx.tools_manager.auth.login()
    response = login_response.json()

    # Verify login success
    assert response["sid"] is not None

    # Perform logout
    configured_auth_ctx.tools_manager.auth.logout()



# @pytest.mark.parametrize("login_data", [
#     {"username": "admin", "password": "admin_pass"},
# ])
# def test_pool_creation(framework_context, login_data):
#     # Login with parametrized data
#     framework_context.tools_manager.auth.login(login_data)
#
#     # Create pools using pools tools
#     pool_config = {...}
#     result = framework_context.tools_manager.pools.create_pool(pool_config)
#
#     # Assertions
#     assert result["status"] == "success"
#
#     # Cleanup
#     framework_context.tools_manager.auth.logout()


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
