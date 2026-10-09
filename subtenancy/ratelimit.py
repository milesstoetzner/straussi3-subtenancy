def client_ip(request):
    """
    Returns the real client IP for django-ratelimit (used via RATELIMIT_IP_META_KEY, see settings).

    Behind a reverse proxy every request arrives with the proxy's address in REMOTE_ADDR, so keying on it would
    throttle all users together. The first address of X-Forwarded-For is the one the proxy received the connection
    from. This is only safe when a reverse proxy in front of the app overwrites that header, which is why it is
    enabled with SUBTENANCY_TRUST_X_FORWARDED_FOR.
    """

    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
