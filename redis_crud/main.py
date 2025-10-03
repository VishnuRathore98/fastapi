from fastapi import FastAPI, HTTPException, status
from pydantic import UUID4
from redis_om import get_redis_connection, HashModel

redis = get_redis_connection(
    host="localhost",
    port="6379",
    decode_responses=True
)

app = FastAPI()

class Product(HashModel):
    product_name: str
    product_description: str
    product_price: float
    product_quantity: int

    class Meta:
        database = redis


@app.get("/get/{id}")
def get_product(id: UUID4):
    product = Product.get(id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Not found")
    return product.model_dump()

@app.get("/get")
def get_products():
    products=[]
    for pk in Product.all_pks():
        p = Product.get(pk)
        products.append(p.model_dump())
    return products


@app.post("/create")
def create_product(product: Product):
    product = Product(**product.model_dump())
    product.save()
    return {"id":product.pk}

@app.put("/update/{id}")
def update_product(product: Product):
    pass

@app.patch("/patch/{id}")
def patch_product():
    pass

@app.delete("/delete/{id}")
def delete_product(id:UUID4):
    Product.delete(id)
    return {"message": "product deleted successfully."}


