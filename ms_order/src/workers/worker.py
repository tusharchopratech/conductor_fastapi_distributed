import random
import requests
from conductor.client.worker.worker_task import worker_task
from database import get_db, Order
from envs import BASE_URL_MS_WAREHOUSE
from datetime import datetime
import time
import os
import threading
import multiprocessing

@worker_task(task_definition_name='submit_an_order_to_warehouse')
def submit_an_order_to_warehouse(order_id: str) -> str:
    db = next(get_db())
    
    unplaced_order = db.query(Order).filter(Order.id == order_id).first()    
    data = {
        "order_id": unplaced_order.id,
        "product_names": unplaced_order.product_names.split(",")
    }
    
    # if random.randint(0,1) == 1:
        # raise Exception("Oops some Fake random Exception occured.")
    # response = requests.post(BASE_URL_MS_WAREHOUSE+"accept-order", json=data)
    # response.raise_for_status()
    
    ts = datetime.now()
    print("-------------xx--------------")
    print(f"Yoo I run - {ts} for {order_id}")
    print(multiprocessing.current_process())
    print(multiprocessing.get_start_method())
    t_id = threading.get_ident()
    print(f"Work process ID: {os.getpid()}, Thread ID: {t_id}")
    
    time.sleep(15)
    return "123"
    

@worker_task(task_definition_name='get_order_status_from_warehouse')
def get_order_status_from_warehouse(order_id: str) -> str:
    print("---------------------------")
    
    print(multiprocessing.current_process())
    print(multiprocessing.get_start_method())
    t_id = threading.get_ident()
    print(f"Work process ID: {os.getpid()}, Thread ID: {t_id}")
    print("--------------xx-------------")

@worker_task(task_definition_name='order_picker_outbox')
def order_picker_outbox() -> str:
    ts = datetime.now()
    print(f"I'm a outbox function call at - {ts}")
    
    return "123"