import pytest
from django.test import Client


@pytest.mark.django_db
def test_healthz_reports_ok():
    r = Client().get('/healthz')
    assert r.status_code == 200
    assert r.content == b'ok\n'                    # only up/down, no internal detail
    assert 'text/plain' in r['Content-Type']
