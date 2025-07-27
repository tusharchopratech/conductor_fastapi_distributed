import logging
import multiprocessing
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from envs import CONDUCTOR_BASE_URL, CONDUCTOR_KEY_ID, CONDUCTOR_KEY_SECRET
from workers.worker import *

logger = logging.getLogger(__name__)


configuration = Configuration(
    base_url=CONDUCTOR_BASE_URL,
    authentication_settings=AuthenticationSettings(
        key_id=CONDUCTOR_KEY_ID, key_secret=CONDUCTOR_KEY_SECRET
    ),
)


def setup_workers():
    task_handler = TaskHandler(configuration=configuration, scan_for_annotated_workers=True)
    multiprocessing.set_start_method("fork", force=True)
    task_handler.start_processes()
    multiprocessing.set_start_method("spawn", force=True)
    logger.info("Worker Ready Execution!")
