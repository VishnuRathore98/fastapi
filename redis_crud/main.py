from fastapi import FastAPI
from pydantic import UUID4
from redis_om import get_redis_connection, HashModel

redis = get_redis_connection(
    host="",
    port="",
    password="",
    decode_resposes=True
)

app = FastAPI()

class Product(HashModel):
    product_name: str
    product_description: str
    product_price: float
    product_quantity: int

    class Meta:
        database = redis


@app.get("/get_product/{id}")
def get_product(id: UUID4):
    pass

@app.post("create_product")
def create_product(product: Product):
    pass

@app.put("update_product/{id}")
def update_product(product: Product):
    pass

@app.patch("patch_product/{id}")
def patch_product():
    pass

@app.delete("delete_product/{id}")
def delete_product(id:UUID4):
    pass
