import json
import logging
import multiprocessing
from conductor.client.orkes_clients import OrkesClients
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from conductor.client.http.models import StartWorkflowRequest
from envs import CONDUCTOR_BASE_URL, CONDUCTOR_KEY_ID, CONDUCTOR_KEY_SECRET
from workers.worker import *

logger = logging.getLogger(__name__)


configuration = Configuration(
    base_url=CONDUCTOR_BASE_URL,
    authentication_settings=AuthenticationSettings(
        key_id=CONDUCTOR_KEY_ID, key_secret=CONDUCTOR_KEY_SECRET
    ),
)


def register_workflows(conductor_workerflows):
    clients = OrkesClients(configuration=configuration)
    metadata_client = clients.get_metadata_client()
    for workflow_path in conductor_workerflows:
        with open(workflow_path, "r") as file:
            data = json.load(file)
        metadata_client.register_workflow_def(workflow_def=data, overwrite=True)
    logger.info("Workflows registered!")


# https://orkes.io/blog/task-level-resilience/


def setup_task_workers():
    task_handler = TaskHandler(configuration=configuration, scan_for_annotated_workers=True)
    multiprocessing.set_start_method("fork", force=True)
    task_handler.start_processes()
    multiprocessing.set_start_method("spawn", force=True)
    logger.info("Worker Ready Execution!")


def run_startup_workflows():
    clients = OrkesClients(configuration=configuration)
    workflow_client = clients.get_workflow_client()
    request = StartWorkflowRequest(
        name="order_picker_outbox_workflow",
        version=1,
        idempotency_key="some_key",
        idempotency_strategy="RETURN_EXISTING",
    )
    workflow_id = workflow_client.start_workflow(start_workflow_request=request)
    logger.info(f"Outbox Workflow Id:{workflow_id}")
