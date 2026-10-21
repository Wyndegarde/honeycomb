from httpx import AsyncClient

REVIEW = {"name": "Excession", "author": "Iain M. Banks", "rating": 5}


async def test_list_reviews_empty(client: AsyncClient):
    resp = await client.get("/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_review(client: AsyncClient):
    resp = await client.post("/reviews", json=REVIEW)
    assert resp.status_code == 201
    body = resp.json()
    assert isinstance(body["id"], int)
    assert {k: body[k] for k in REVIEW} == REVIEW


async def test_create_review_invalid_rating(client: AsyncClient):
    for rating in (9, -1):
        resp = await client.post("/reviews", json={**REVIEW, "rating": rating})
        assert resp.status_code == 422
        assert resp.json()["detail"][0]["loc"] == ["body", "rating"]
    assert (await client.get("/reviews")).json() == []


async def test_create_review_missing_field(client: AsyncClient):
    resp = await client.post("/reviews", json={"name": "x"})
    assert resp.status_code == 422


async def test_create_review_name_too_long(client: AsyncClient):
    resp = await client.post("/reviews", json={**REVIEW, "name": "x" * 2001})
    assert resp.status_code == 422


async def test_list_reviews_after_create(client: AsyncClient):
    created = (await client.post("/reviews", json=REVIEW)).json()
    resp = await client.get("/reviews")
    assert resp.status_code == 200
    assert resp.json() == [created]


async def test_get_review(client: AsyncClient):
    created = (await client.post("/reviews", json=REVIEW)).json()
    resp = await client.get(f"/reviews/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


async def test_get_review_not_found(client: AsyncClient):
    resp = await client.get("/reviews/999999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Review not found"}


async def test_get_review_invalid_id(client: AsyncClient):
    resp = await client.get("/reviews/abc")
    assert resp.status_code == 422


async def test_tests_are_isolated(client: AsyncClient):
    # Earlier tests created rows; none should have leaked through the rollback.
    assert (await client.get("/reviews")).json() == []
