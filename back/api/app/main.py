from fastapi import FastAPI

app = FastAPI(title="Nomoni API", version="0.1.0")


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hola Mundo"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
