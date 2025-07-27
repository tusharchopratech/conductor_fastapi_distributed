import requests
import logging
from conductor.client.worker.worker_task import worker_task
from database import get_db, Order
from envs import BASE_URL_MS_SUPPLIER, BASE_URL_MS_ORDER

logger = logging.getLogger(__name__)


@worker_task(task_definition_name="poll_supplier")
def poll_supplier(warehouse_tracking_id: str) -> str:

    db = next(get_db())
    unfinished_order = db.query(Order).filter(Order.id == warehouse_tracking_id).first()
    response = requests.get(f"{BASE_URL_MS_SUPPLIER}order/{unfinished_order.supplier_tracking_id}")
    response.raise_for_status()
    supplier_order_status = response.json()["status"]

    logger.info(
        f"Order warehouse_tracking_id: {warehouse_tracking_id} Supplier State - {supplier_order_status}"
    )
    if supplier_order_status == "DONE":
        unfinished_order.status = "DONE"
        db.flush()

        response = requests.put(
            f"{BASE_URL_MS_ORDER}order",
            json={"warehouse_tracking_id": warehouse_tracking_id, "status": supplier_order_status},
        )
        response.raise_for_status()

        db.commit()
        logger.info("Completeing warehouse_tracking_id: {warehouse_tracking_id}")
        return "STOP"

    db.close()
    return "KEEP_GOING"
