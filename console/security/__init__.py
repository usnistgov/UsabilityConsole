import random
import string
import hashlib

__PREFIX = "3IYbBurXMX";
__KEY_LENGTH = 32


def compute_hash(data: str):
    return hashlib.sha3_256(data.encode()).hexdigest()


def generate_api_key():
    key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(__KEY_LENGTH)])
    generated_api_key = ''.join([__PREFIX, '.', key])
    return generated_api_key


def generate_api_key_hash(api_key):
    generated_api_key_hash = compute_hash(api_key)
    return ''.join([__PREFIX, '.', generated_api_key_hash])


api_key = generate_api_key()
print(api_key)
hashed_api_key = generate_api_key_hash(api_key)
print(hashed_api_key)
print(hashed_api_key.encode())
