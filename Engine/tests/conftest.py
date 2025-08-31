from sys import path
from logging import getLogger, Logger, DEBUG
from pathlib import Path
path.insert(0, str(Path(__file__).parent.parent.resolve()))

from pytest import TempPathFactory, fixture

from fastapi.testclient import TestClient

from StreamStorm.api.fastapi_app import app

@fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
     
        
@fixture(autouse=True, scope="session")
def configure_logger() -> None:
    logger: Logger = getLogger("tests")
    logger.setLevel(DEBUG)
    
    
@fixture(scope="session")
def user_data_dir(tmp_path_factory: TempPathFactory):
    return tmp_path_factory.mktemp("user_data_dir")