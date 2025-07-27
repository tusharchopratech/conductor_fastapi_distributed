import uuid
import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends, HTTPException
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
    return {"service_name": SERVICE_NAME, "message": f"Hello from pod_{str(POD_ID)}"}


@app.post("/order")
async def create_order(order_payload: OrderPayload, db: Session = Depends(get_db)):
    order = Order(
        id=str(uuid.uuid4()), product_names=",".join(order_payload.product_names), status="NEW"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"tracking_id": order.id}


@app.get("/order/{tracking_id}")
async def get_order(tracking_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == tracking_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order id `{tracking_id}` not found.")
    return {
        "tracking_id": order.id,
        "product_names": order.product_names.split(","),
        "status": order.status,
    }


class UpdateOrderPayload(BaseModel):
    warehouse_tracking_id: str
    status: str


@app.put("/order")
async def update_order(update_order_payload: UpdateOrderPayload, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .filter(Order.warehouse_tracking_id == update_order_payload.warehouse_tracking_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Warehouse order id `{update_order_payload.warehouse_tracking_id}` not found.",
        )
    order.status = update_order_payload.status
    db.commit()
    return {"status": "success"}


if __name__ == "__main__":
    register_workflows(
        conductor_workerflows=[
            "src/workers/order_picker_workflow.json",
            "src/workers/order_processing_workflow.json",
        ]
    )
    setup_task_workers()
    run_startup_workflows()
    uvicorn.run("main:app", host="0.0.0.0", port=80)
