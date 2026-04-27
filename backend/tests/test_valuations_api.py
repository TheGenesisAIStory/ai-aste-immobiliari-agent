from __future__ import annotations


def test_valuation_crud(client, sample_payload: dict) -> None:
    created = client.post("/valuations", json=sample_payload)
    assert created.status_code == 200
    body = created.json()
    valuation_id = body["id"]
    assert body["city"] == "Torino"
    assert body["total_cost"] == 123000

    listed = client.get("/valuations")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [valuation_id]

    detail = client.get(f"/valuations/{valuation_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == valuation_id

    deleted = client.delete(f"/valuations/{valuation_id}")
    assert deleted.status_code == 200
    assert client.get(f"/valuations/{valuation_id}").status_code == 404
    assert client.get("/valuations").json() == []


def test_valuation_404(client) -> None:
    assert client.get("/valuations/999").status_code == 404
    assert client.delete("/valuations/999").status_code == 404
