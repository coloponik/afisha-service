from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from afisha.exceptions import (
    DashboardUnavailableError,
    DomainError,
    EventNotFoundError,
    ForbiddenError,
    PaymentUnavailableError,
    SeatAlreadyReservedError,
    SeatAlreadySoldError,
    SeatsNotFoundError,
    LockTimeoutError
)

DOMAIN_ERROR_RESPONSES: dict[type[DomainError], tuple[int, str]] = {
    DashboardUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Analytics is temporarily unavailable"
    ),
    EventNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Event not found"
    ),
    ForbiddenError: (
        status.HTTP_403_FORBIDDEN,
        "User is not the event organizer"
    ),
    SeatAlreadyReservedError: (
        status.HTTP_409_CONFLICT,
        "Seat is already reserved"
    ),
    SeatAlreadySoldError: (
        status.HTTP_409_CONFLICT,
        "Seat is already sold"
    ),
    SeatsNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "Seat not found"
    ),
    LockTimeoutError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Event service temporarily unavailable"
    ),
    PaymentUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "Payment service is temporarily unavailable"
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
