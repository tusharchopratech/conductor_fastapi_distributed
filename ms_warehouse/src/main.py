import uuid
import requests
import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Order
from workers.utils import setup_workers
from envs import BASE_URL_MS_SUPPLIER


SERVICE_NAME = "WAREHOUSE"
POD_ID = str(random.randint(1, 100))

app = FastAPI(
    title="Order Service",
    version="0.0.1",
)


class OrderPayload(BaseModel):
    order_id: str
    product_names: List[str]


@app.get("/")
async def root():
    return {"service_name": SERVICE_NAME, "message": f"Hello from pod_{str(POD_ID)}"}


@app.post("/order")
async def order(order_payload: OrderPayload, db: Session = Depends(get_db)):

    order = Order(
        id=str(uuid.uuid4()),
        name=",".join(order_payload.product_names),
        order_tracking_id=order_payload.order_id,
        status="PENDING",
    )
    db.add(order)
    db.flush()
    data = {"warehouse_tracking_id": order.id, "product_names": order.name.split(",")}
    response = requests.post(BASE_URL_MS_SUPPLIER + "order", json=data)
    response.raise_for_status()

    order.supplier_tracking_id = response.json()["tracking_id"]
    db.commit()
    return {"status": "success", "tracking_id": order.id}


if __name__ == "__main__":
    setup_workers()
    uvicorn.run("main:app", host="0.0.0.0", port=80)
