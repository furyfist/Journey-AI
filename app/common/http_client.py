import httpx


def build_async_client(timeout: float = 30.0, retries: int = 2) -> httpx.AsyncClient:
    transport = httpx.AsyncHTTPTransport(retries=retries)
    return httpx.AsyncClient(transport=transport, timeout=timeout)
