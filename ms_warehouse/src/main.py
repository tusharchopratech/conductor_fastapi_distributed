import uuid
import asyncio
import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, Product
from workers.utils import setup_workers

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
    return {"service_name": SERVICE_NAME,"message": f"Hello from pod_{str(POD_ID)}"}


@app.post("/accept-order")
async def order(order_payload: OrderPayload, db: Session = Depends(get_db)):    
    for product_name in order_payload.product_names:
        product = Product(
            id = str(uuid.uuid4()), 
            name=product_name, 
            status="PENDING",
            order_id=order_payload.order_id
            )
        db.add(product)
    db.commit()
    return {"status":"success", "order_id": order_payload.order_id}


@app.get("/poll-vendor")
async def poll_mib():
    await asyncio.sleep(3)
    options = ["DONE", "PENDING", "STARTED"]
    status = options[random.randint(0, 2)]    
    result = {"search_status": status}
    print(f"Poll endpoint runs {result}")
    return result


if __name__ == "__main__":
    setup_workers()
    uvicorn.run("main:app", host="0.0.0.0", port=80)