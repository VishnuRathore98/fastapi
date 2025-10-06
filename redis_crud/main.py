from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import UUID4, BaseModel
from redis_om import Field, get_redis_connection, HashModel

redis = get_redis_connection(
    host="localhost",
    port="6379",
    decode_responses=True
)

app = FastAPI()

class Product(HashModel):
    product_name: str = Field(index=True, full_text_search=True) #indexing for full text search
    product_description: str
    product_price: float = Field(index=True) #indexing for quick search
    product_quantity: int

    class Meta:
        database = redis

class ProductUpdate(BaseModel):
    product_name: str
    product_description: str
    product_price: float
    product_quantity: int

    

class ProductPatch(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_price: Optional[float] = None
    product_quantity: Optional[int] = None

class Session(HashModel):
    user_id: str
    data: str

    class Meta:
        global_ttl = 600  # 10 mins for all sessions
        database = redis

@app.post("/sessions/")
def create_session(user_id:str, data:str):
    s = Session(user_id=user_id, data=data)
    s.save() # this session expires in 10 minutes
    return {"session_id": s.pk}

@app.get("/sessions/{session_id}")
def get_session(session_id:str):
    s = Session.get(session_id)
    if s is None:
        return {"error":"session expired"}
    
    return s.dict()


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

# Update the existing by replacing 
@app.put("/update/{id}")
def update_product(id: str, product_data: ProductUpdate):
    
    product = Product.get(id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product.product_name = product_data.product_name
    product.product_description = product_data.product_description
    product.product_price = product_data.product_price
    product.product_quantity = product_data.product_quantity
    product.save()

    return product

@app.patch("/patch/{id}")
def patch_product(id: str, product_data: ProductPatch):

    product = Product.get(id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)

    product.save()

    return product

@app.delete("/delete/{id}")
def delete_product(id:UUID4):
    Product.delete(id)
    return {"message": "product deleted successfully."}

@app.get("/products/search")
def search_products(q: str | None = None, min_price: float  | None = None, max_price: float | None = None):
    
    query = Product.find()

    if q:
        query = query.query(Product.product_name % q)

    if min_price is not None:
        query = query.filter(Product.product_price >= min_price)

    if max_price is not None:
        query = query.filter(Product.product_price <= max_price)

    return [p.dict() for p in query.all()]

