from fastapi import status, FastAPI, Request
from fastapi.responses import JSONResponse

from afisha.exceptions import (
    DomainError,
    SeatAlreadyReservedError,
    SeatsNotFoundError,
    PaymentUnavailableError,
    EventNotFoundError
)

DOMAIN_ERROR_RESPONSES: dict[type[DomainError], tuple[int, str]] = {
    SeatAlreadyReservedError: (
        status.HTTP_409_CONFLICT,
        "Seat is already reserved"
    ),
    SeatsNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Seat not found"
    ),
    PaymentUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Payment service is unavailable now"
    ),
    EventNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Event not found"
    )
}


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_exception_handler(_: Request, exc: DomainError) -> JSONResponse:

        status_code, message = _get_domain_error_response(exc)

        return JSONResponse(
            status_code=status_code,
            content={"detail": message}
        )


def _get_domain_error_response(exc: DomainError) -> tuple[int, str]:
    for error_type, response in DOMAIN_ERROR_RESPONSES.items():
        if isinstance(exc, error_type):
            return response
    return status.HTTP_400_BAD_REQUEST, "Unknown error"
