# tests/test_file_transfer_app.py

import pytest
import os
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "file_transfer_project.settings")
settings.configure()


from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from file_transfer_app.models import FileTransfer
from file_transfer_app.forms import FileTransferForm
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def authenticated_client(client, user):
    client.login(username='testuser', password='testpassword')
    return client

@pytest.fixture
def test_file(db, user):
    return FileTransfer.objects.create(
        title='Test File',
        uploader=user,
        file='test.txt'  # This should be a valid file path for testing
    )

def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'file_transfer_app/home.html' in [template.name for template in response.templates]

def test_user_login_view_authenticated(authenticated_client):
    response = authenticated_client.get(reverse('user_login'))
    assert response.status_code == 302  # Redirects to home for authenticated user

def test_user_login_view_valid_credentials(authenticated_client):
    response = authenticated_client.post(reverse('user_login'), {'username': 'testuser', 'password': 'testpassword'})
    assert response.status_code == 302  # Successful login redirects to home

def test_user_login_view_invalid_credentials(client, user):
    client.logout()
    response = client.post(reverse('user_login'), {'username': 'testuser', 'password': 'wrongpassword'})
    assert response.status_code == 200  # Expect a status code of 200
    messages = list(get_messages(response.wsgi_request))
    
    # Check the error message when the user is not already logged in
    if not user.is_authenticated:
        assert len(messages) == 1
        assert str(messages[0]) == "Username or Password is incorrect."
    else:
        # If the user is already logged in, expect a different message
        assert len(messages) == 1
        assert str(messages[0]) == "Already logged in."
