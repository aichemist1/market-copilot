from __future__ import annotations

import base64
import hashlib
import hmac
import os


SCRYPT_PREFIX = "scrypt"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_KEY_LENGTH = 64


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_KEY_LENGTH,
    )
    salt_value = base64.urlsafe_b64encode(salt).decode("utf-8")
    hash_value = base64.urlsafe_b64encode(derived).decode("utf-8")
    return f"{SCRYPT_PREFIX}${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt_value}${hash_value}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, n, r, p, salt_value, hash_value = password_hash.split("$", maxsplit=5)
    except ValueError:
        return False

    if scheme != SCRYPT_PREFIX:
        return False

    salt = base64.urlsafe_b64decode(salt_value.encode("utf-8"))
    expected = base64.urlsafe_b64decode(hash_value.encode("utf-8"))
    actual = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=len(expected),
    )
    return hmac.compare_digest(actual, expected)
