
class DomainError(Exception):
    pass


class BookingError(DomainError):
    pass


class SeatAlreadyReservedError(BookingError):
    pass


class SeatsNotFoundError(BookingError):
    pass

