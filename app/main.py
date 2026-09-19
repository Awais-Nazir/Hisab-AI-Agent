from fastapi import FastAPI


app = FastAPI(title="Hisab Agent")


@app.get("/")
def test():
    return {"message": "welcome to Hisab Agent API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
