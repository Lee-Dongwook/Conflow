import ipaddress
import os
from urllib.parse import urlparse

from fastapi import Request


def is_trust(s: str | None) -> bool:
    if not s:
        return False
    if s == "localhost":
        return True
    
    try: 
        ip = ipaddress.ip_address(s.strip("[]"))
        if ip.is_loopback:
            return True
        
        trusted_env = os.environ.get("TRUSTED_NETWORKS", "")
        if trusted_env:
            for network_str in trusted_env.split(","):
                try:
                    if ip in ipaddress.ip_network(network_str.strip()):
                        return True
                except ValueError:
                    continue
        return False
    except ValueError:
        return False

def is_local(request: Request) -> bool:
    if request.headers.get("x-Forwarded-For") or request.headers.get("X-Real-IP"):
        return False
    
    h = request.url.hostname
    c = request.client.host if request.client else None

    if c and not is_trust(c):
        return False
    
    if h:
        return is_trust(h)
    
    return c == "::1"

def is_cross_origin(request:Request) -> bool:
    origin = request.headers.get("Origin")
    if not origin:
        return False
    
    origin_parsed = urlparse(origin)
    request_url = request.url

    is_same_origin = (
        origin_parsed.scheme == request_url.scheme and
        origin_parsed.hostname == request_url.hostname and
        (origin_parsed.port or (80 if origin_parsed.scheme == "http" else 443)) ==
        (request_url.port or (80 if request_url.scheme == "http" else 443))
    )

    return not is_same_origin

def get_cookie_samesite(request:Request, is_local: bool) -> str:
    if is_local:
        return "lax"
    
    if is_cross_origin(request):
        return "none"
    
    return "lax"
