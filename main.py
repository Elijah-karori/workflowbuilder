from fastapi import FastAPI
from app.api.v1.endpoints import workflows, abac
from app.core.database import engine, Base

# This is for demonstration purposes. In a production setup with Alembic,
# you would typically not call create_all() like this.
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workflow Builder API")

app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(abac.router, prefix="/api/v1/abac", tags=["abac"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Workflow Builder API"}
