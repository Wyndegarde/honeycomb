from httpx import AsyncClient

from tests.test_media import create_media

REVIEW = {"rating": 5, "body": "A masterpiece of ships arguing."}


async def test_get_review_missing(client: AsyncClient):
    media = await create_media(client)
    resp = await client.get(f"/media/{media['id']}/review")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Review not found"}


async def test_put_review_creates_then_replaces(client: AsyncClient):
    media = await create_media(client)
    url = f"/media/{media['id']}/review"

    resp = await client.put(url, json=REVIEW)
    assert resp.status_code == 200
    first = resp.json()
    assert first["media_id"] == media["id"]
    assert {k: first[k] for k in REVIEW} == REVIEW

    resp = await client.put(url, json={"rating": 3})
    assert resp.status_code == 200
    assert resp.json()["id"] == first["id"]
    assert resp.json()["rating"] == 3
    assert resp.json()["body"] is None

    assert (await client.get(url)).json() == resp.json()


async def test_review_appears_on_media(client: AsyncClient):
    media = await create_media(client)
    review = (await client.put(f"/media/{media['id']}/review", json=REVIEW)).json()
    assert (await client.get(f"/media/{media['id']}")).json()["review"] == review


async def test_put_review_invalid_rating(client: AsyncClient):
    media = await create_media(client)
    for rating in (9, -1):
        resp = await client.put(f"/media/{media['id']}/review", json={"rating": rating})
        assert resp.status_code == 422
        assert resp.json()["detail"][0]["loc"] == ["body", "rating"]


async def test_put_review_media_not_found(client: AsyncClient):
    resp = await client.put("/media/999999/review", json=REVIEW)
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Media not found"}


async def test_delete_review(client: AsyncClient):
    media = await create_media(client)
    url = f"/media/{media['id']}/review"
    await client.put(url, json=REVIEW)
    assert (await client.delete(url)).status_code == 204
    assert (await client.get(url)).status_code == 404
    assert (await client.delete(url)).status_code == 404


async def test_deleting_media_deletes_review(client: AsyncClient):
    media = await create_media(client)
    url = f"/media/{media['id']}/review"
    await client.put(url, json=REVIEW)
    await client.delete(f"/media/{media['id']}")
    assert (await client.get(url)).status_code == 404
