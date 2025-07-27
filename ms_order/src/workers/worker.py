import requests
import logging
from conductor.client.worker.worker_task import worker_task
from conductor.client.http.models import StartWorkflowRequest
from conductor.client.orkes_clients import OrkesClients
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from database import get_db, Order
from envs import BASE_URL_MS_WAREHOUSE, CONDUCTOR_BASE_URL, CONDUCTOR_KEY_ID, CONDUCTOR_KEY_SECRET


logger = logging.getLogger(__name__)

configuration = Configuration(
    base_url=CONDUCTOR_BASE_URL,
    authentication_settings=AuthenticationSettings(
        key_id=CONDUCTOR_KEY_ID, key_secret=CONDUCTOR_KEY_SECRET
    ),
)

clients = OrkesClients(configuration=configuration)
workflow_client = clients.get_workflow_client()


@worker_task(task_definition_name="order_picker_outbox")
def order_picker_outbox() -> str:
    db = next(get_db())
    unplaced_order = db.query(Order).filter(Order.status == "NEW").first()
    if unplaced_order:
        workflow_id = workflow_client.start_workflow(
            start_workflow_request=StartWorkflowRequest(
                name="order_submission_workflow",
                version=1,
                input={"order_id": str(unplaced_order.id)},
            )
        )
        unplaced_order.workflow_id = workflow_id
        unplaced_order.status = "PENDING"
        db.commit()
        logger.info(
            f"Order Processing Workflow Started | 'workflow_id' : {workflow_id} | 'order_id' : {unplaced_order.id}"
        )
    else:
        logger.info("No new order found!")
    db.close()
    return "KEEP_GOING"


@worker_task(task_definition_name="submit_an_order_to_warehouse")
def submit_an_order_to_warehouse(order_id: str) -> str:
    db = next(get_db())

    order = db.query(Order).filter(Order.id == order_id).first()
    data = {"order_id": order.id, "product_names": order.product_names.split(",")}

    response = requests.post(BASE_URL_MS_WAREHOUSE + "order", json=data)
    response.raise_for_status()

    warehouse_tracking_id = response.json()["tracking_id"]
    order.warehouse_tracking_id = warehouse_tracking_id

    logger.info(
        f"Warehouse Request Accepted | 'order_id' : {order_id} | 'warehouse_tracking_id' : {warehouse_tracking_id}"
    )
    
    db.commit()
    db.close()
    return {"warehouse_tracking_id": warehouse_tracking_id}
