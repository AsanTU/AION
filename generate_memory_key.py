from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("memory.key", "wb") as key_file:
    key_file.write(key)