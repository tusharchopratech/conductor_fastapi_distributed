import requests
import random
from conductor.client.worker.worker_task import worker_task
from database import get_db, Product

@worker_task(task_definition_name='submit_an_products_to_vendor')
def submit_an_order_to_warehouse(order_id: str) -> str:
    
    db = next(get_db())
    
    products = db.query(Product).filter(Product.status == "PENDING").all()
    unshipped_products = []
    for product in products:
        unshipped_products.append(
            {
                "name": product.name,
                "product_id": product.id
            }
        )
    
    if random.random():
        raise Exception("Oops some Fake random Exception occured.")
    
    # requests.post