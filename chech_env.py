import os
from dotenv import load_dotenv

load_dotenv()

print("=== Environment variables (repr) ===")
print(f"DATABASE_TYPE: {repr(os.getenv('DATABASE_TYPE'))}")
print(f"POSTGRES_HOST: {repr(os.getenv('POSTGRES_HOST'))}")
print(f"POSTGRES_PORT: {repr(os.getenv('POSTGRES_PORT'))}")
print(f"POSTGRES_USER: {repr(os.getenv('POSTGRES_USER'))}")
print(f"POSTGRES_PASSWORD: {repr(os.getenv('POSTGRES_PASSWORD'))}")
print(f"POSTGRES_DATABASE: {repr(os.getenv('POSTGRES_DATABASE'))}")