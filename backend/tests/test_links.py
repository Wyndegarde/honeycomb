from httpx import AsyncClient

from tests.test_media import MEDIA, create_media


async def link(client: AsyncClient, a: int, b: int, **body):
    return await client.post(
        f"/media/{a}/links", json={"media_id": b, "themes": ["Grief"], **body}
    )


async def test_add_and_list_link_both_ends(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client, title="Hyperion")

    resp = await link(client, b["id"], a["id"], note="both sad")
    assert resp.status_code == 201
    assert resp.json() == {
        "media_id": a["id"],
        "title": a["title"],
        "themes": ["grief"],
        "note": "both sad",
    }

    from_a = (await client.get(f"/media/{a['id']}/links")).json()
    assert from_a == [
        {
            "media_id": b["id"],
            "title": "Hyperion",
            "themes": ["grief"],
            "note": "both sad",
        }
    ]


async def test_add_link_errors(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client)
    assert (await link(client, a["id"], b["id"])).status_code == 201
    assert (await link(client, b["id"], a["id"])).status_code == 409
    assert (await link(client, a["id"], a["id"])).status_code == 422
    assert (await link(client, a["id"], 9999)).status_code == 404
    assert (await link(client, 9999, a["id"])).status_code == 404
    for bad in ({"themes": []}, {"themes": [" "]}, {"themes": ["x"] * 21 + ["y"]}):
        resp = await client.post(
            f"/media/{a['id']}/links", json={"media_id": b["id"], **bad}
        )
        assert resp.status_code == 422
    assert (await client.get("/media/abc/links")).status_code == 422


async def test_themes_are_shared_case_insensitively(client: AsyncClient):
    a, b, c = [await create_media(client) for _ in range(3)]
    await link(client, a["id"], b["id"], themes=["War", "war ", "Loss"])
    await link(client, a["id"], c["id"], themes=["WAR"])
    got = (await client.get(f"/media/{a['id']}/links")).json()
    assert [g["themes"] for g in got] == [["loss", "war"], ["war"]]


async def test_list_links_404_and_paging(client: AsyncClient):
    assert (await client.get("/media/9999/links")).status_code == 404
    a, b, c = [await create_media(client) for _ in range(3)]
    await link(client, a["id"], b["id"])
    await link(client, a["id"], c["id"])
    page = (await client.get(f"/media/{a['id']}/links?limit=1&offset=1")).json()
    assert [p["media_id"] for p in page] == [c["id"]]


async def test_patch_link(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client)
    await link(client, a["id"], b["id"], note="old")
    url = f"/media/{b['id']}/links/{a['id']}"

    resp = await client.patch(url, json={"themes": ["Hope"]})
    assert resp.status_code == 200
    assert resp.json()["themes"] == ["hope"]
    assert resp.json()["note"] == "old"

    resp = await client.patch(url, json={"note": None})
    assert resp.json()["note"] is None
    assert resp.json()["themes"] == ["hope"]

    assert (await client.patch(url, json={"themes": []})).status_code == 422
    assert (await client.patch(url, json={"themes": None})).status_code == 422
    assert (
        await client.patch(f"/media/{a['id']}/links/9999", json={})
    ).status_code == 404


async def test_delete_link(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client)
    await link(client, a["id"], b["id"])
    assert (await client.delete(f"/media/{a['id']}/links/{b['id']}")).status_code == 204
    assert (await client.delete(f"/media/{a['id']}/links/{b['id']}")).status_code == 404
    assert (await client.get(f"/media/{b['id']}/links")).json() == []
    # Themes are kept; re-linking works
    assert (await link(client, a["id"], b["id"])).status_code == 201


async def test_delete_media_removes_its_links(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client)
    await link(client, a["id"], b["id"])
    assert (await client.delete(f"/media/{a['id']}")).status_code == 204
    assert (await client.get(f"/media/{b['id']}/links")).json() == []


async def test_create_media_with_links(client: AsyncClient):
    a = await create_media(client)
    resp = await client.post(
        "/media",
        json={
            **MEDIA,
            "title": "New",
            "links": [{"media_id": a["id"], "themes": ["AI"]}],
        },
    )
    assert resp.status_code == 201
    assert "links" not in resp.json()
    got = (await client.get(f"/media/{resp.json()['id']}/links")).json()
    assert [(g["media_id"], g["themes"]) for g in got] == [(a["id"], ["ai"])]


async def test_create_media_with_bad_links_saves_nothing(client: AsyncClient):
    a = await create_media(client)
    ok = {"media_id": a["id"], "themes": ["x"]}
    for links, code in (
        ([ok, {"media_id": 9999, "themes": ["x"]}], 404),
        ([ok, ok], 422),
        ([{"media_id": a["id"], "themes": []}], 422),
    ):
        resp = await client.post("/media", json={**MEDIA, "links": links})
        assert resp.status_code == code
    assert len((await client.get("/media")).json()) == 1


async def test_link_invalid_path_ids(client: AsyncClient):
    body = {"media_id": 1, "themes": ["x"]}
    assert (await client.post("/media/abc/links", json=body)).status_code == 422
    assert (await client.patch("/media/abc/links/1", json={})).status_code == 422
    assert (await client.patch("/media/1/links/abc", json={})).status_code == 422
    assert (await client.delete("/media/abc/links/1")).status_code == 422
    assert (await client.delete("/media/1/links/abc")).status_code == 422
