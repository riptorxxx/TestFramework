from dataclasses import dataclass
from typing import Optional
from .base_models import BaseConfig


@dataclass
class AuthConfig(BaseConfig):
    username: Optional[str] = None
    password: Optional[str] = None
    remember: Optional[bool] = None

    _api_mapping = {
        'username': 'login',
        'password': 'password',
        'remember': 'remember'
    }
