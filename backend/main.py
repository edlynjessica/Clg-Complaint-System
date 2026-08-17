from fastapi import FastAPI

from routes.auth import router as auth_router

app = FastAPI(title="College Maintenance System")

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "College Maintenance System API is running"}