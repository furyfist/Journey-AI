from typing import Annotated

import httpx
from fastapi import Depends, Request
from supabase import AsyncClient


def get_db(request: Request) -> AsyncClient:
    return request.app.state.db


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


DBDep = Annotated[AsyncClient, Depends(get_db)]
HttpDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
