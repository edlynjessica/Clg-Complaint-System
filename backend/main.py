from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.complaints import router as complaints_router

app = FastAPI(title="College Maintenance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(complaints_router)


@app.get("/")
def root():
    return {"message": "College Maintenance System API is running"}