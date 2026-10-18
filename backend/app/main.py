from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.get("/reviews")
async def get_all_reviews():
    return {"reviews": []}
