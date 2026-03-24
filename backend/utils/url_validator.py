import ipaddress
import socket
from urllib.parse import urlparse
from functools import lru_cache

@lru_cache(maxsize=256)
def _resolve_hostname(hostname: str) -> str | None:
    """Cached DNS lookup — prevents 2s × N URL lookups from stalling the pipeline."""
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        ip = socket.gethostbyname(hostname)
        socket.setdefaulttimeout(old_timeout)
        return ip
    except (socket.gaierror, socket.timeout, OSError):
        return None

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.hostname:
        return False

    ip = _resolve_hostname(parsed.hostname)
    
    if ip is None:
        # DNS failed — still allow the URL (better to try scraping than silently drop)
        return True
    
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return False
    except ValueError:
        return True

    return True
