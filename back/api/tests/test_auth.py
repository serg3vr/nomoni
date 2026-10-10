GARBAGE_TOKEN = "Bearer eyJhbGciOiJIUzI1NiJ9.bm90LXJlYWw.yolO"


async def test_register_returns_token(client):
    response = await client.post(
        "/auth/register",
        json={"email": "a@mail.com", "password": "secreta123", "name": "Ana"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_register_normalizes_email_and_can_login(client):
    await client.post(
        "/auth/register",
        json={"email": "B@mail.com ", "password": "secreta123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "b@mail.com", "password": "secreta123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dup@mail.com", "password": "secreta123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/auth/register",
        json={"email": "c@mail.com", "password": "secreta123"},
    )
    response = await client.post(
        "/auth/login",
        data={"username": "c@mail.com", "password": "incorrecta"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_unknown_email_same_error(client):
    response = await client.post(
        "/auth/login",
        data={"username": "ghost@mail.com", "password": "secreta123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_me_returns_user_without_password(client):
    register = await client.post(
        "/auth/register",
        json={"email": "d@mail.com", "password": "secreta123", "name": "Dana"},
    )
    token = register.json()["access_token"]
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "d@mail.com"
    assert body["name"] == "Dana"
    assert body["currency"] == "MXN"
    assert "password_hash" not in body


async def test_me_requires_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_rejects_garbage_token(client):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": GARBAGE_TOKEN},
    )
    assert response.status_code == 401


async def test_patch_me_updates_profile(client):
    register = await client.post(
        "/auth/register",
        json={"email": "f@mail.com", "password": "secreta123"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(
        "/auth/me",
        json={"name": "Fabio", "currency": "COP"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["currency"] == "COP"
