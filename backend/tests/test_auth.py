import os
import sys
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException, status

from app import models
from app.auth import (
    verify_password,
    get_password_hash,
    get_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    pwd_context
)


@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict('os.environ', {
        'SECRET_KEY': 'test-secret-key',
        'JWT_EXPIRE_MINUTES': '30'
    }):
        yield


@pytest.fixture
def db_():
    db = MagicMock()
    return db


@pytest.fixture
def sample_user():
    hashed_password = get_password_hash("testpassword")
    return models.User(
        username="testuser",
        hashed_password=hashed_password
    )


@pytest.fixture
def valid_token():
    data = {"sub": "testuser"}
    return create_access_token(data,
                               timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


# Test cases for verify_password
def test_verify_password_correct(sample_user):
    assert verify_password("testpassword", sample_user.hashed_password) is True


def test_verify_password_incorrect(sample_user):
    assert verify_password("wrongpassword",
                           sample_user.hashed_password) is False


# Test cases for get_password_hash
def test_get_password_hash():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert pwd_context.verify(password, hashed)


# Test cases for get_user
def test_get_user_found(db_, sample_user):
    db_.query.return_value.filter.return_value.first.return_value = sample_user
    result = get_user(db_, "testuser")
    assert result == sample_user


def test_get_user_not_found(db_):
    db_.query.return_value.filter.return_value.first.return_value = None
    result = get_user(db_, "nonexistent")
    assert result is None


# Test cases for authenticate_user
def test_authenticate_user_success(db_, sample_user):
    db_.query.return_value.filter.return_value.first.return_value = sample_user
    result = authenticate_user(db_, "testuser", "testpassword")
    assert result == sample_user


def test_authenticate_user_wrong_password(db_, sample_user):
    db_.query.return_value.filter.return_value.first.return_value = sample_user
    result = authenticate_user(db_, "testuser", "wrongpassword")
    assert result is False


def test_authenticate_user_not_found(db_):
    db_.query.return_value.filter.return_value.first.return_value = None
    result = authenticate_user(db_, "nonexistent", "testpassword")
    assert result is False


# Test cases for create_access_token
def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)


def test_create_access_token_with_expiry():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_get_current_user_valid_token(sample_user, valid_token):
    # Mock just the get_user function to return our sample user
    with patch('app.auth.get_user', return_value=sample_user), \
        patch('app.auth.oauth2_scheme',
              new_callable=AsyncMock) as mock_scheme:
        mock_scheme.return_value = valid_token
        user = await get_current_user(token=valid_token)
        assert user == sample_user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    with patch('app.auth.oauth2_scheme',
               new_callable=AsyncMock) as mock_scheme:
        mock_scheme.return_value = "invalidtoken"
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalidtoken")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_missing_subject(db_):
    # Create token without 'sub' field
    data = {}
    token_without_sub = create_access_token(data)

    with patch('app.auth.oauth2_scheme',
               new_callable=AsyncMock) as mock_scheme:
        mock_scheme.return_value = token_without_sub
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token_without_sub)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# Test environment variables
def test_environment_variables():
    assert SECRET_KEY is not None
    assert isinstance(SECRET_KEY, str)
    assert ALGORITHM == "HS256"
    assert ACCESS_TOKEN_EXPIRE_MINUTES == 30
