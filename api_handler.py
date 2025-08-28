import keyring
import pybithumb

def get_api_keys():
    connect_key = keyring.get_password('bithumb', 'connect_key')
    secret_key = keyring.get_password('bithumb', 'secret_key')
    if not connect_key or not secret_key:
        return None, None
    return connect_key, secret_key

def set_api_keys(connect_key, secret_key):
    keyring.set_password('bithumb', 'connect_key', connect_key)
    keyring.set_password('bithumb', 'secret_key', secret_key)

def get_bithumb_client():
    connect_key, secret_key = get_api_keys()
    if not connect_key or not secret_key:
        return None
    return pybithumb.Bithumb(connect_key, secret_key)