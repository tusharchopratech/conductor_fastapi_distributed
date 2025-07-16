import json
import multiprocessing
from conductor.client.orkes_clients import OrkesClients
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from conductor.client.http.models import StartWorkflowRequest
from workers.worker import *


configuration = Configuration(
    base_url='https://developer.orkescloud.com',
    authentication_settings=AuthenticationSettings(
        key_id='',
        key_secret=''))


def register_workflows(conductor_workerflows):
    clients = OrkesClients(configuration=configuration)
    metadata_client = clients.get_metadata_client()
    for workflow_path in conductor_workerflows:
        with open(workflow_path, 'r') as file:
            data = json.load(file)
        metadata_client.register_workflow_def(workflow_def=data, overwrite=True)
    print("Workflows registered!")
    
# https://orkes.io/blog/task-level-resilience/

def setup_task_workers():  
    task_handler = TaskHandler(
        configuration=configuration,
        scan_for_annotated_workers=True   
    )
    multiprocessing.set_start_method('fork', force=True)
    task_handler.start_processes()
    multiprocessing.set_start_method('spawn', force=True)
    print("Worker Ready Execution!")
    
def run_startup_workflows():
    clients = OrkesClients(configuration=configuration)
    workflow_client = clients.get_workflow_client()
    request = StartWorkflowRequest(
        name='order_picker_outbox_workflow', 
        version=1,
        idempotency_key="some_key",
        idempotency_strategy="RETURN_EXISTING"
    )
    workflow_id = workflow_client.start_workflow(start_workflow_request=request)
    print(f"Outbox Workflow Id:{workflow_id}")