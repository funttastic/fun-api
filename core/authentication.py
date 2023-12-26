import os
import re
import bcrypt
import base64
from getpass import getpass


def generate_passphrase_hash(passphrase):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passphrase.encode('utf-8'), salt)


def verify_passphrase(stored_passphrase_hash, provided_passphrase):
    return bcrypt.checkpw(provided_passphrase.encode('utf-8'), stored_passphrase_hash)


def define_password():
    passphrase_minimal_length = 4
    max_attempts = 5

    for attempt in range(max_attempts):
        passphrase = getpass(f"   New passphrase [Attempt {attempt+1}/{max_attempts}]: ")

        if len(passphrase) < passphrase_minimal_length:

            print(f"\n   [!] The passphrase must have at least {passphrase_minimal_length} digits. Please try again.\n")

            if attempt == max_attempts - 1:
                print("\n   [!] You have reached the maximum number of attempts. Please try again later.\n")
                exit(0)
        else:
            for confirmation_attempt in range(max_attempts):

                confirm_passphrase = getpass(
                    f"\n   Confirm your passphrase [Attempt {confirmation_attempt+1}/{max_attempts}]: "
                )

                if passphrase == confirm_passphrase:
                    return passphrase

                elif confirmation_attempt == max_attempts - 1:
                    print("\n   [!] The passwords do not match, check if everything is ok with your keyboard...\n")

                    exit(0)
                else:
                    print("\n   [!] The passwords provided are different. Please try again.")


def authenticate(properties, password):
    server_private_key_password_hash = properties.get(
        "hummingbot.gateway.certificates.server_private_key_password_hash"
    )

    if server_private_key_password_hash == '<password_hash>' or len(
            server_private_key_password_hash
    ) == 0 or server_private_key_password_hash is None or re.fullmatch(r"^\s*$", server_private_key_password_hash):

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n   ===============     AUTHENTICATION - FUNTTASTIC HUMMINGBOT CLIENT     ===============\n")

        print("   This is the first time you will start the server. Please define a passphrase.\n")

        if len(password) > 0:
            new_passphrase = password
        else:
            new_passphrase = define_password()

        hashed_passphrase = generate_passphrase_hash(new_passphrase)

        properties.set("hummingbot.gateway.certificates.server_private_key_password_hash", hashed_passphrase)

        return True
    else:
        i = 0
        while True:
            if i == 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n   ===============     AUTHENTICATION - FUNTTASTIC HUMMINGBOT CLIENT     ===============\n")

            if len(password) > 0:
                provided_passphrase = password
            else:
                provided_passphrase = getpass(f"   Enter your password to access [Attempt {i+1}/3]: ")

            passphrase_to_binary = base64.b64decode(server_private_key_password_hash)
            correct = verify_passphrase(passphrase_to_binary, provided_passphrase)

            if correct:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n   Access granted.\n")
                return True
            else:
                print("\n   Incorrect password. Please try again.\n")

            i += 1
            if i >= 3:
                print("\n   Access denied. Incorrect password.\n   You have exhausted your 3 consecutive attempts.\n")
                return False
