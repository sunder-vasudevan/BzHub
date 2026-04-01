from fastapi import FastAPI
from inventory import router as inventory_router
from hr import router as hr_router
from pos import router as pos_router
from visitor import router as visitor_router
from payroll import router as payroll_router

app = FastAPI()

app.include_router(inventory_router)
app.include_router(hr_router)
app.include_router(pos_router)
app.include_router(visitor_router)
app.include_router(payroll_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI backend!"}
