
class DomainError(Exception):
    pass


class BookingError(DomainError):
    pass


class PaymentUnavailableError(BookingError):
    pass


class SeatAlreadyReservedError(BookingError):
    pass


class SeatsNotFoundError(BookingError):
    pass


class EventError(DomainError):
    pass


class EventNotFoundError(EventError):
    pass
