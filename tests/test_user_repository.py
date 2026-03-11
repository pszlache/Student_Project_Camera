import os
import sqlite3
import tempfile

import pytest

from core.repositories.user_repository import UserRepository
from database import db as db_module


# Fixture: Temporary Database
@pytest.fixture
def temp_db(monkeypatch):
    temp_dir = tempfile.TemporaryDirectory()
    temp_db_path = os.path.join(temp_dir.name, "test.db")

    # Patch DB_PATH to temporary DB
    monkeypatch.setattr(db_module, "DB_PATH", temp_db_path)

    # Initialize tables
    db_module.init_db()

    yield temp_db_path

    temp_dir.cleanup()


# Tests
def test_add_and_get_user(temp_db):
    repo = UserRepository()

    repo.add_user("user@example.com")

    emails = repo.get_notification_emails(cam_id=0)

    assert "user@example.com" in emails


def test_camera_specific_user(temp_db):
    repo = UserRepository()

    repo.add_user("cam1@example.com", camera_id=1)
    repo.add_user("global@example.com", camera_id=None)

    emails_cam1 = repo.get_notification_emails(1)
    emails_cam2 = repo.get_notification_emails(2)

    assert "cam1@example.com" in emails_cam1
    assert "cam1@example.com" not in emails_cam2

    assert "global@example.com" in emails_cam1
    assert "global@example.com" in emails_cam2


def test_disable_notifications(temp_db):
    repo = UserRepository()

    repo.add_user("user@example.com")
    repo.disable_notifications("user@example.com")

    emails = repo.get_notification_emails(cam_id=0)

    assert "user@example.com" not in emails


def test_duplicate_user_returns_false(temp_db):
    repo = UserRepository()

    result1 = repo.add_user("dup@example.com")
    result2 = repo.add_user("dup@example.com")

    assert result1 is True
    assert result2 is False
