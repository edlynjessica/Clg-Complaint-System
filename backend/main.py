from fastapi import FastAPI

app = FastAPI(title="College Maintenance System")


@app.get("/")
def root():
    return {"message": "College Maintenance System API is running"}