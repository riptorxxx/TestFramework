class CookieManager:
    """Класс для управления cookie"""
    def __init__(self):
        self._cookies = {}

    def get_current_cookies(self) -> dict:
        return self._cookies.copy()

    def update_from_response(self, response):
        if 'Set-Cookie' in response.headers:
            new_cookies = self.parse_set_cookie_header(
                response.headers.get_list('Set-Cookie')
            )
            self._cookies.update(new_cookies)

    @staticmethod
    def parse_set_cookie_header(set_cookie_header) -> dict:
        """Parse Set-Cookie header into cookie dictionary"""
        cookies = {}
        if not set_cookie_header:
            return cookies

        cookie_headers = set_cookie_header if isinstance(set_cookie_header, list) else [set_cookie_header]

        for cookie_str in cookie_headers:
            # Parse specific cookies we're interested in
            for cookie_name in ['BAUMSID', 'jwt_access', 'jwt_refresh']:
                if f'{cookie_name}=' in cookie_str:
                    value = cookie_str.split(f'{cookie_name}=')[1].split(';')[0]
                    cookies[cookie_name] = value

        return cookies

    @staticmethod
    def format_cookie_header(cookies: dict) -> str:
        """Format cookies dictionary into Cookie header string"""
        return '; '.join([f"{k}={v}" for k, v in cookies.items()])
