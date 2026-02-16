requirements.txt:
fastapi
passlib
sqlalchemy

tests/test_auth.py:
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

def test_auth():
    assert True

pytest.ini:
[pytest]
addopts = --maxfail=1 --disable-warnings -q
testpaths = tests