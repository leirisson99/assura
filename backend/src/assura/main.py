from fastapi import FastAPI

app = FastAPI(title="Assura")


@app.get("/saude")
def verificar_saude() -> dict[str, str]:
    return {"situacao": "ok"}
