from fastapi import FastAPI
from api.execute.endpoints import router as execute_router
from api.monitor.endpoints import router as monitor_router
from api.adapt.endpoints import router as adapt_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(adapt_router, prefix="/adaptation_options", tags=["adapt"])
app.include_router(monitor_router, prefix="/monitor", tags=["monitor"])
app.include_router(execute_router, prefix="/execute", tags=["execute"])

