


import os

class Config:
    # ------------------------ Uber app global variables  ------------------------

    REDIRECT_URI = "http://127.0.0.1:5000/callback"
    AUTH_BASE = "https://sandbox-login.uber.com"
    AUTH_URL = f"{AUTH_BASE}/oauth/v2/authorize"
    TOKEN_URL = f"{AUTH_BASE}/oauth/v2/token"

    CORE_API_BASE = "https://test-api.uber.com"

    SECRET_KEY = os.urandom(24)
    
    
    
