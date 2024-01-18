from argparse import Namespace
from pathlib import Path

import pytest
from google_api_service_helper import GoogleDrive, GoogleSheets
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.clients.soho import Soho
from lms.db.uow import UnitOfWork
from lms.logic.distribute_homeworks import Distributor
from lms.utils.settings import SettingStorage


@pytest.fixture
def google_keys() -> str:
    return """
    {
        "type": "service_account",
        "project_id": "test-python",
        "private_key_id": "something",
        "private_key": "something",
        "client_email": "test@example.com",
        "client_id": 0,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/"
    }
    """


@pytest.fixture
def google_key_json_file(google_keys: str, tmp_path: Path) -> Path:
    d = tmp_path / "test"
    d.mkdir()

    f = d / "google_keys.json"
    f.write_text(google_keys)
    yield f


@pytest.fixture
def google_sheets(args: Namespace) -> GoogleSheets:
    # return GoogleSheets(google_keys=args.google_keys)
    return None


@pytest.fixture
def google_drive(args: Namespace) -> GoogleDrive:
    # return GoogleDrive(google_keys=args.google_keys)
    return None


@pytest.fixture
async def get_distributor(
    sessionmaker: async_sessionmaker[AsyncSession],
    soho: Soho,
    google_drive: GoogleDrive,
    google_sheets: GoogleSheets,
):
    def new_distributor() -> Distributor:
        uow = UnitOfWork(sessionmaker=sessionmaker)
        return Distributor(
            uow=uow,
            google_drive=google_drive,
            google_sheets=google_sheets,
            soho=soho,
            settings=SettingStorage(uow=uow),
        )

    return new_distributor
