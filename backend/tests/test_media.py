from httpx import AsyncClient

MEDIA = {
    "title": "Excession",
    "creator": "Iain M. Banks",
    "media_type": "book",
    "year": 1996,
    "description": None,
}


async def create_media(client: AsyncClient, **overrides) -> dict:
    resp = await client.post("/media", json={**MEDIA, **overrides})
    assert resp.status_code == 201
    return resp.json()


async def test_list_media_empty(client: AsyncClient):
    resp = await client.get("/media")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_media(client: AsyncClient):
    body = await create_media(client)
    assert isinstance(body["id"], int)
    assert {k: body[k] for k in MEDIA} == MEDIA
    assert body["review"] is None


async def test_create_media_invalid(client: AsyncClient):
    for bad in ({"media_type": "vinyl"}, {"title": ""}, {"title": "x" * 2001}):
        resp = await client.post("/media", json={**MEDIA, **bad})
        assert resp.status_code == 422
    assert (await client.post("/media", json={"title": "x"})).status_code == 422
    assert (await client.get("/media")).json() == []


async def test_get_media(client: AsyncClient):
    created = await create_media(client)
    resp = await client.get(f"/media/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


async def test_get_media_not_found(client: AsyncClient):
    resp = await client.get("/media/999999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Media not found"}


async def test_get_media_invalid_id(client: AsyncClient):
    assert (await client.get("/media/abc")).status_code == 422


async def test_search_and_filter(client: AsyncClient):
    await create_media(client)
    await create_media(client, title="Dune", creator="Frank Herbert")
    await create_media(client, title="Alien", creator="Ridley Scott", media_type="film")

    titles = lambda r: sorted(m["title"] for m in r.json())
    assert titles(await client.get("/media", params={"q": "banks"})) == ["Excession"]
    assert titles(await client.get("/media", params={"q": "dun"})) == ["Dune"]
    assert titles(await client.get("/media", params={"type": "film"})) == ["Alien"]
    assert titles(await client.get("/media", params={"type": "book"})) == [
        "Dune",
        "Excession",
    ]
    assert len((await client.get("/media", params={"limit": 1})).json()) == 1


async def test_search_treats_wildcards_literally(client: AsyncClient):
    await create_media(client, title="100% Wolf")
    await create_media(client, title="a_b")
    await create_media(client, title="axb")

    titles = lambda r: sorted(m["title"] for m in r.json())
    assert titles(await client.get("/media", params={"q": "%"})) == ["100% Wolf"]
    assert titles(await client.get("/media", params={"q": "a_b"})) == ["a_b"]


async def test_update_media(client: AsyncClient):
    created = await create_media(client)
    resp = await client.patch(f"/media/{created['id']}", json={"year": 1997})
    assert resp.status_code == 200
    assert resp.json()["year"] == 1997
    assert resp.json()["title"] == "Excession"
    assert (await client.patch("/media/999999", json={"year": 1})).status_code == 404


async def test_update_media_rejects_null_required_fields(client: AsyncClient):
    created = await create_media(client)
    for field in ("title", "creator", "media_type"):
        resp = await client.patch(f"/media/{created['id']}", json={field: None})
        assert resp.status_code == 422
    # Optional fields can still be cleared
    resp = await client.patch(f"/media/{created['id']}", json={"year": None})
    assert resp.status_code == 200
    assert resp.json()["year"] is None


async def test_delete_media(client: AsyncClient):
    created = await create_media(client)
    assert (await client.delete(f"/media/{created['id']}")).status_code == 204
    assert (await client.get(f"/media/{created['id']}")).status_code == 404
    assert (await client.delete(f"/media/{created['id']}")).status_code == 404


async def test_tests_are_isolated(client: AsyncClient):
    # Earlier tests created rows; none should have leaked through the rollback.
    assert (await client.get("/media")).json() == []
