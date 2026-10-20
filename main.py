from fastapi import FastAPI

import models
from router import auth, transaction
from database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(transaction.router)


@app.get("/", include_in_schema=False)
def health_check():
    return {"message": "Server is up and running..."}
