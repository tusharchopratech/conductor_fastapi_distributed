import json
import multiprocessing
from conductor.client.orkes_clients import OrkesClients
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from workers.worker import *


configuration = Configuration(
    base_url='https://developer.orkescloud.com',
    authentication_settings=AuthenticationSettings(
        key_id='',
        key_secret=''))



def setup_workers():  
    task_handler = TaskHandler(
        configuration=configuration,
        scan_for_annotated_workers=True   
    )
    multiprocessing.set_start_method('fork', force=True)
    task_handler.start_processes()
    multiprocessing.set_start_method('spawn', force=True)
    print("Worker Ready Execution!")