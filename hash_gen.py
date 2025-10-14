import bcrypt
hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt(rounds=12)).decode()
print(hash)
