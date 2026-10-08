from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def make_item(**kwargs):
    data = {"name": "Laptop", "description": "test", "price": 500.0, "quantity": 3}
    data.update(kwargs)
    r = client.post("/items", json=data)
    assert r.status_code == 201
    return r.json()


def test_root():
    assert client.get("/").status_code == 200


def test_create_and_get():
    item = make_item()
    r = client.get(f"/items/{item['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Laptop"


def test_create_bad_price():
    r = client.post("/items", json={"name": "x", "price": 0, "quantity": 1})
    assert r.status_code == 422


def test_list():
    make_item(name="Mouse")
    r = client.get("/items")
    assert r.status_code == 200
    assert any(i["name"] == "Mouse" for i in r.json())


def test_search():
    make_item(name="Keyboard")
    assert client.get("/items/search", params={"keyword": "keyb"}).status_code == 200
    assert client.get("/items/search", params={"keyword": "nothing-here"}).status_code == 404


def test_update():
    item = make_item()
    r = client.put(f"/items/{item['id']}", json={"quantity": 9})
    assert r.status_code == 200
    assert r.json()["quantity"] == 9
    assert r.json()["name"] == "Laptop"


def test_update_with_nulls_keeps_old_values():
    item = make_item()
    r = client.put(f"/items/{item['id']}", json={"name": None, "price": None})
    assert r.status_code == 200
    assert r.json()["name"] == "Laptop"
    assert r.json()["price"] == 500.0


def test_update_can_clear_description():
    item = make_item()
    r = client.put(f"/items/{item['id']}", json={"description": None})
    assert r.status_code == 200
    assert r.json()["description"] is None


def test_delete():
    item = make_item()
    assert client.delete(f"/items/{item['id']}").status_code == 200
    assert client.get(f"/items/{item['id']}").status_code == 404
    assert client.delete(f"/items/{item['id']}").status_code == 404
