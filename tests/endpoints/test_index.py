"""Tests for non-API routes (index and error handling)."""


def test_get_index_returns_200(client):
    resp = client.get('/')
    assert resp.status_code == 200


def test_get_index_returns_html(client):
    resp = client.get('/')
    assert 'text/html' in resp.content_type


def test_get_index_contains_app_title(client):
    assert b'Pflanzen' in client.get('/').data


def test_non_api_path_not_found_returns_html_404(client):
    resp = client.get('/nonexistent-page')
    assert resp.status_code == 404
    assert 'text/html' in resp.content_type
