import os
from dotenv import load_dotenv
from pathlib import Path

# Check current directory
print(f"Current working directory: {os.getcwd()}")

# Check if .env file exists
env_path = Path(".env")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    print(f".env file size: {env_path.stat().st_size} bytes")
    print("\n.env file contents:")
    print("-" * 30)
    with open(".env") as f:
        content = f.read()
        print(content)
    print("-" * 30)

# Load the .env file
print(f"\nLoading .env from: {env_path.absolute()}")
load_dotenv()

print("\nEnvironment variables after loading:")
print(f"PINECONE_API_KEY: {os.getenv('PINECONE_API_KEY', 'NOT FOUND')}")
print(f"PINECONE_ENVIRONMENT: {os.getenv('PINECONE_ENVIRONMENT', 'NOT FOUND')}")
print(f"PINECONE_INDEX_NAME: {os.getenv('PINECONE_INDEX_NAME', 'NOT FOUND')}")