from fastapi import FastAPI
from routes import router

app = FastAPI (title = "RAG + Banco em memoria")

app.include_router(router)

