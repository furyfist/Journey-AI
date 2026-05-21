from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import JourneyAIError, RateLimitError, TripNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TripNotFoundError)
    async def trip_not_found_handler(request: Request, exc: TripNotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError):
        return JSONResponse(status_code=429, content={"detail": exc.message})

    @app.exception_handler(JourneyAIError)
    async def journey_error_handler(request: Request, exc: JourneyAIError):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
