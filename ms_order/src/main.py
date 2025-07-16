import uuid
import asyncio
import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Order
from workers.utils import register_workflows, setup_task_workers, run_startup_workflows

SERVICE_NAME = "ORDER"
POD_ID = str(random.randint(1, 100))

app = FastAPI(
    title="Order Service",
    version="0.0.1",
)

class OrderPayload(BaseModel):
    product_names: List[str]
    
@app.get("/")
async def root():
    return {"service_name": SERVICE_NAME,"message": f"Hello from pod_{str(POD_ID)}"}



@app.post("/order")
async def order(order_payload: OrderPayload, db: Session = Depends(get_db)):    
    order = Order(id = str(uuid.uuid4()), product_names=",".join(order_payload.product_names), status="NEW")
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order_id": order.id}


@app.get("/poll-mib")
async def poll_mib():
    await asyncio.sleep(3)
    options = ["DONE", "PENDING", "STARTED"]
    status = options[random.randint(0, 2)]    
    result = {"search_status": status}
    print(f"Poll endpoint runs {result}")
    return result


if __name__ == "__main__":
    register_workflows(conductor_workerflows=[
        "src/workers/order_picker_outbox.json",
        "src/workers/order_workflow_main.json"
    ])
    setup_task_workers()
    run_startup_workflows()
    uvicorn.run("main:app", host="0.0.0.0", port=80)