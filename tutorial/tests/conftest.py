from icecream import ic
import pytest
from flaskr import create_app

@pytest.fixture()
def app():
    app = create_app()

    # other setup can go there
    
    yield app

    """
    you can do anything after yield
    """
    
    # clean up / reset resources here
    
@pytest.fixture() 
def client(app):
    return app.test_client()

# @pytest.fixture()
# def runner(app):
#     return app.test_cli_runner()

# def test_request_example(client):
#     response = client.get("/")
#     ic(response.data)