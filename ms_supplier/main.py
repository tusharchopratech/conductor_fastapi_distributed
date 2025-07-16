import logging
import requests
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from conductor.client.http.models import StartWorkflowRequest
from conductor.client.metadata_client import MetadataClient
from conductor.client.orkes_clients import OrkesClients


configuration = Configuration(base_url='https://developer.orkescloud.com',
                                  authentication_settings=AuthenticationSettings(
                                      key_id='',
                                        key_secret=''))

configuration.apply_logging_config(level=logging.INFO)


clients = OrkesClients(configuration=configuration)
workflow_client = clients.get_workflow_client()
    
data = {
    "product_names": ["Iphone", "Table"]
}
response = requests.post("http://localhost:80/order", json=data)
response.raise_for_status()
order_id = response.json()["order_id"]

request = StartWorkflowRequest(
    name='order_submission_workflow', 
    version=1, 
    input={"order_id": order_id}
    )
workflow_id = workflow_client.start_workflow(start_workflow_request=request)

print(f"order_id: {order_id} | workflow_id:{workflow_id}")