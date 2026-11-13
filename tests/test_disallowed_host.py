"""
A request with a foreign Host header is answered with 400 and does not reach the console log (scanners hitting the
server IP with arbitrary host names filled the log with tracebacks).

The check looks at the logger's configuration rather than at caplog: pytest attaches its capture handler to every
non-propagating logger, so caplog would see the record even though no real handler does.
"""
import logging


def test_foreign_host_is_400(client):
    assert client.get('/healthz', HTTP_HOST='str3.ext.selfnet.de').status_code == 400


def test_disallowed_host_logger_is_silent():
    logger = logging.getLogger('django.security.DisallowedHost')
    assert not logger.propagate
    assert [type(h) for h in logger.handlers] == [logging.NullHandler]
    assert logging.getLogger('django.security.SuspiciousOperation').propagate   # other security events still log
