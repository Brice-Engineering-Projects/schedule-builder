from fastapi import FastAPI

from schedule_builder.api.router import api_router

app = FastAPI(title="Schedule Builder", version="0.1.0")

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Schedule Builder API"}
