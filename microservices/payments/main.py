import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host = "redis-18645.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port = 18645,
    password = "lJqnnjZcgNrlUT2oZjv4QsgIB07c1cTJ",
    decode_responses = True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int 
    status: str

    class Meta:
        database = redis

@app.get("/")
def main():
    return {"message":"Hello from payments!"}

@app.get("/orders/{pk}")
def get_product(pk:str):
    return Order.get(pk)

@app.post("/orders/")
async def place_order(request:Request, background_tasks:BackgroundTasks):
    body = await request.json()
    print(body)
    req = requests.get(f"http://localhost:8000/products/{body['product_id']}")
    product = req.json()

    order = Order(
        product_id = body['product_id'],
        price = product['price'],
        fee = 0.2 * product['price'],
        total = 1.2 * product['price'],
        quantity = body['quantity'],
        status = 'pending'
    )

    order.save()
    
    background_tasks.add_task(order_completed, order)

    return order.json()




def order_completed(order:Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
