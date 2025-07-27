import uuid
import asyncio
import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Order
from datetime import datetime, timedelta


SERVICE_NAME = "SUPPLIER"
POD_ID = str(random.randint(1, 100))

app = FastAPI(
    title="Order Service",
    version="0.0.1",
)


class OrderPayload(BaseModel):
    warehouse_tracking_id: str
    product_names: List[str]


@app.get("/")
async def root():
    return {"service_name": SERVICE_NAME, "message": f"Hello from pod_{str(POD_ID)}"}


@app.post("/order")
async def order(order_payload: OrderPayload, db: Session = Depends(get_db)):
    created_ts = datetime.now()
    completed_ts = created_ts + timedelta(seconds=60)
    order = Order(
        id=str(uuid.uuid4()),
        name=",".join(order_payload.product_names),
        warehouse_tracking_id=order_payload.warehouse_tracking_id,
        status="PENDING",
        created_at=created_ts,
        completed_at=completed_ts,
    )
    db.add(order)
    db.commit()
    return {"status": "success", "tracking_id": order.id}


@app.get("/order/{tracking_id}")
async def get_order(tracking_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == tracking_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order id `{tracking_id}` not found.")

    if order.completed_at < datetime.now():
        order.status = "DONE"
        db.commit()
        db.refresh(order)
    return {"tracking_id": order.id, "product_names": order.name.split(","), "status": order.status}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80)
