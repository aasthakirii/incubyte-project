def auth(token):
    return {"Authorization": f"Bearer {token}"}

def test_admin_can_create_and_user_can_list(client, admin_token, user_token):
    created = client.post("/api/vehicles", headers=auth(admin_token), json={
        "make": "Honda", "model": "Civic", "category": "Sedan", "price": 18000, "quantity": 3
    })
    assert created.status_code == 201
    listed = client.get("/api/vehicles", headers=auth(user_token))
    assert listed.status_code == 200
    assert listed.json()[0]["make"] == "Honda"

def test_vehicle_creation_requires_admin(client, user_token):
    response = client.post("/api/vehicles", headers=auth(user_token), json={
        "make": "Honda", "model": "Civic", "category": "Sedan", "price": 18000, "quantity": 3
    })
    assert response.status_code == 403

def test_authentication_is_required(client):
    assert client.get("/api/vehicles").status_code == 401

def test_search_filters_make_and_price(client, admin_token, user_token):
    headers = auth(admin_token)
    for make, model, price in [("Toyota", "Corolla", 22000), ("Honda", "Civic", 18000)]:
        client.post("/api/vehicles", headers=headers, json={
            "make": make, "model": model, "category": "Sedan", "price": price, "quantity": 1
        })
    result = client.get("/api/vehicles/search?make=toyota&min_price=20000", headers=auth(user_token))
    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0]["make"] == "Toyota"

def test_purchase_decrements_stock_and_rejects_zero(client, admin_token, user_token):
    create = client.post("/api/vehicles", headers=auth(admin_token), json={
        "make": "Mazda", "model": "3", "category": "Sedan", "price": 20000, "quantity": 1
    })
    vehicle_id = create.json()["id"]
    purchase = client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=auth(user_token))
    assert purchase.status_code == 200
    assert purchase.json()["quantity"] == 0
    empty = client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=auth(user_token))
    assert empty.status_code == 409

def test_restock_is_admin_only(client, admin_token, user_token, vehicle_id):
    denied = client.post(f"/api/vehicles/{vehicle_id}/restock", headers=auth(user_token), json={"quantity": 2})
    assert denied.status_code == 403
    accepted = client.post(f"/api/vehicles/{vehicle_id}/restock", headers=auth(admin_token), json={"quantity": 4})
    assert accepted.status_code == 200
    assert accepted.json()["quantity"] == 6

def test_admin_can_update_and_delete(client, admin_token, vehicle_id):
    updated = client.put(f"/api/vehicles/{vehicle_id}", headers=auth(admin_token), json={"price": 24000})
    assert updated.status_code == 200
    assert updated.json()["price"] == 24000
    deleted = client.delete(f"/api/vehicles/{vehicle_id}", headers=auth(admin_token))
    assert deleted.status_code == 204
    assert client.get(f"/api/vehicles/{vehicle_id}", headers=auth(admin_token)).status_code == 404
