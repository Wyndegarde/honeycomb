from httpx import AsyncClient


async def test_health(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}
