from fastapi import FastAPI

import models
from router import auth
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)


@app.get("/", include_in_schema=False)
def health_check():
    return {"message": "Server is up and running..."}
