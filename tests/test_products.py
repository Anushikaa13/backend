def test_create_product(client, auth_headers):
    product_data = {
        "id": 1,
        "name": "Test Product",
        "price": 9.99,
        "quantity": 100,
        "description": "This is a test product description"
    }
    response = client.post("/products", json=product_data, headers=auth_headers)

    # see the validation error details
    if response.status_code == 422:
        print(response.json()) 
        
    assert response.status_code in [200, 201]