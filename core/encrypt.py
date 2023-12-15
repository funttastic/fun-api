import bcrypt


def generate_passphrase_hash(passphrase):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passphrase.encode('utf-8'), salt)


def verify_passphrase(stored_passphrase_hash, provided_passphrase):
    return bcrypt.checkpw(provided_passphrase.encode('utf-8'), stored_passphrase_hash)
