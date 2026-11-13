"""
A request with a foreign Host header is answered with 400 and does not reach the console log (scanners hitting the
server IP with arbitrary host names filled the log with tracebacks).

The check looks at the logging configuration rather than at caplog or the logger's handler list: pytest attaches
its own capture handler to every non-propagating logger, so both would show the record although no real handler
receives it.
"""
import logging

from django.conf import settings


def test_foreign_host_is_400(client):
    assert client.get('/healthz', HTTP_HOST='str3.ext.selfnet.de').status_code == 400


def test_disallowed_host_logger_is_silent():
    assert settings.LOGGING['loggers']['django.security.DisallowedHost'] == {'handlers': ['null'], 'propagate': False}
    assert settings.LOGGING['handlers']['null'] == {'class': 'logging.NullHandler'}
    assert not logging.getLogger('django.security.DisallowedHost').propagate
    assert logging.getLogger('django.security.SuspiciousOperation').propagate   # other security events still log
