class AuthenticationError(Exception):
    """Custom exception for authentication errors"""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

    def __str__(self):
        base_message = f"Authentication Error: {self.message}"
        if self.status_code:
            base_message += f" (Status: {self.status_code})"
        return base_message
