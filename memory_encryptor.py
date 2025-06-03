import os
import json
import time
from cryptography.fernet import Fernet
from pathlib import Path

BASE = Path.home() / "1man.army" / "memory"
SRC = BASE / "experience_log.json"
ENC = BASE / "experience_log.enc"
KEY_FILE = BASE / "vault.key"

def generate_key():
    """Generate & store encryption key."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    """Load existing encryption key or create a new one."""
    if not KEY_FILE.exists():
        return generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def save_experience(action, result):
    """Log AI experience with timestamp before encryption."""
    new_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "result": result
    }

    try:
        with open(SRC, "r") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append(new_entry)

    with open(SRC, "w") as file:
        json.dump(logs, file, indent=4)

    encrypt_file()  # Auto-encrypt after logging
    print(f"[✅] Experience saved: {new_entry}")

def encrypt_file():
    """Encrypt AI memory securely."""
    key = load_key()
    fernet = Fernet(key)
    with open(SRC, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(ENC, "wb") as f:
        f.write(encrypted)
    os.remove(SRC)  # Delete unencrypted file after securing
    print("[🔐] Memory encrypted successfully.")

def decrypt_file():
    """Decrypt AI memory for retrieval."""
    key = load_key()
    fernet = Fernet(key)
    with open(ENC, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    with open(SRC, "wb") as f:
        f.write(decrypted)
    print("[🔓] Memory decrypted and ready.")

def recall_last_experience():
    """Retrieve most recent AI experience after decryption."""
    decrypt_file()
    try:
        with open(SRC, "r") as file:
            logs = json.load(file)
            last_experience = logs[-1] if logs else "No past experiences recorded."
            print(f"[📜] Last Experience: {last_experience}")
            return last_experience
    except (FileNotFoundError, json.JSONDecodeError):
        return "Memory log empty."

if __name__ == "__main__":
    print("🔐 AI Memory Vault")
    action = input("Type 'log' to save, 'lock' to encrypt, 'unlock' to decrypt, or 'recall' to retrieve last experience: ").strip().lower()

    if action == "log":
        action_details = input("Describe AI action: ")
        result_details = input("What was the outcome? ")
        save_experience(action_details, result_details)
    elif action == "lock":
        encrypt_file()
    elif action == "unlock":
        decrypt_file()
    elif action == "recall":
        recall_last_experience()
    else:
        print("[✖] Invalid command.")