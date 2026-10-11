from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main():
    return {"message": "Hello World"}


@app.get("/reviews")
def get_all_reviews():
    return {"reviews": []}
