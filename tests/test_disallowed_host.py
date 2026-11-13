"""
A request with a foreign Host header is answered with 400 and does not produce an error log entry (scanners hitting
the server IP with arbitrary host names filled the log with tracebacks).
"""
import logging


def test_foreign_host_is_400_without_error_log(client, caplog):
    with caplog.at_level(logging.DEBUG):
        response = client.get('/healthz', HTTP_HOST='str3.ext.selfnet.de')
    assert response.status_code == 400
    assert [r for r in caplog.records if r.name.startswith('django.security')] == []
