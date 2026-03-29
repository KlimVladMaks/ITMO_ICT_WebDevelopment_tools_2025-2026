from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def get_api_status():
    return "API работает!"
