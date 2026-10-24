from httpx import AsyncClient

from tests.test_links import link
from tests.test_media import create_media


async def test_graph_empty(client: AsyncClient):
    resp = await client.get("/graph")
    assert resp.status_code == 200
    assert resp.json() == {"nodes": [], "edges": []}


async def test_graph_nodes_and_edges(client: AsyncClient):
    a = await create_media(client)
    b = await create_media(client, title="Hyperion")
    await create_media(client, title="Lonely")
    await link(client, b["id"], a["id"], note="both sad")

    body = (await client.get("/graph")).json()
    assert {n["title"] for n in body["nodes"]} == {"Excession", "Hyperion", "Lonely"}
    assert "review" not in body["nodes"][0]
    assert body["edges"] == [
        {
            "source": a["id"],
            "target": b["id"],
            "themes": ["grief"],
            "note": "both sad",
        }
    ]
