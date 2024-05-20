from flask import session

def test_home(client):
    response = client.get(f"/")
    # assert b"<title>Home</title>" in response.data
    assert response.status_code == 200

def test_modify_session(client):
    ...