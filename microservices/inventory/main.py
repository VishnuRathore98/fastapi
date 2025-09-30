from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-18645.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=18645,
    password="lJqnnjZcgNrlUT2oZjv4QsgIB07c1cTJ",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/")
def index():
    return {'message':'hello world of microservices!'}

@app.get("/products")
def get_all_products():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)

    return {
        "pk":product.pk,
        "name":product.name,
        "price": product.price,
        "quantity":product.quantity
    }

@app.post("/products")
def create_product(product: Product):
    return product.save()

@app.get("/products/{pk}")
def get_a_product(pk:str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete_product(pk:str):
    return Product.delete(pk)
