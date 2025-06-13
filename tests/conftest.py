""""""
import pytest
from chalice.config import Config
from chalice.local import LocalGateway

import os
os.environ['QUEUE_NAME'] = 'test-input-queue'
os.environ['OUTPUT_QUEUE_NAME'] = 'test-output-queue'

from app import app


@pytest.fixture
def client():
    config = Config.create()
    return LocalGateway(app, config)
