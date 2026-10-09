from django.conf import settings


def client_ip(group, request):
    """
    Rate limit key that returns the real client IP.

    Behind a reverse proxy every request arrives with the proxy's address in REMOTE_ADDR, so keying on it would
    throttle all users together. If SUBTENANCY_TRUST_X_FORWARDED_FOR is enabled the first address of the
    X-Forwarded-For header (the one the proxy received the connection from) is used instead. Only enable this when a
    reverse proxy in front of the app overwrites that header.
    """

    if settings.TRUST_X_FORWARDED_FOR:
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
