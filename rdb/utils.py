import hashlib


def omanghasher(identity):
    return hashlib.sha256(identity.encode()).hexdigest()
