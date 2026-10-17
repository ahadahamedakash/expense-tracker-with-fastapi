from fastapi import FastAPI


from database import engine, SessionLocal
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def bootstrap():
    return {"message": "Server is up and running..."}
