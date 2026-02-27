import ipaddress
import socket
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.hostname:
        return False

    try:
        # 2-second timeout prevents blocking on slow/fresh domains
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        ip = socket.gethostbyname(parsed.hostname)
        socket.setdefaulttimeout(old_timeout)
        
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return False

    except (socket.gaierror, socket.timeout, OSError):
        # DNS failed — still allow the URL (better to try scraping than silently drop)
        return True

    return True
