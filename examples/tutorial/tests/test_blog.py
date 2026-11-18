import pytest

from flaskr.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b'name="q"' in response.data

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


def test_search(client, app):
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
            ("Café de l'Été", "Résumé of the post", 1),
        )
        db.commit()

    response = client.get("/?q=ETE")
    assert "Café de l".encode() in response.data

    response = client.get("/?q=RESUME")
    assert "Café de l".encode() in response.data


def test_search_no_results(client):
    response = client.get("/?q=missing")
    assert b'No posts found for "missing".' in response.data


def test_search_form_on_other_pages(client):
    response = client.get("/auth/login")
    assert b'name="q"' in response.data


def test_search_pagination(client, app):
    with app.app_context():
        db = get_db()
        for day in range(1, 7):
            db.execute(
                "INSERT INTO post (title, body, author_id, created)"
                " VALUES (?, '', 1, ?)",
                (f"paginated {day}", f"2020-01-0{day} 00:00:00"),
            )
        db.commit()

    response = client.get("/?q=paginated")
    assert b"paginated 6" in response.data
    assert b"paginated 2" in response.data
    assert b"paginated 1" not in response.data
    assert response.data.index(b"paginated 6") < response.data.index(b"paginated 2")
    assert b"q=paginated&amp;page=2" in response.data

    response = client.get("/?q=paginated&page=2")
    assert b"paginated 1" in response.data
    assert b"paginated 2" not in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
