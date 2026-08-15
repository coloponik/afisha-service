
class DomainError(Exception):
    pass


class BookingError(DomainError):
    pass


class PaymentUnavailableError(BookingError):
    pass


class SeatAlreadyReservedError(BookingError):
    pass


class SeatAlreadySoldError(BookingError):
    pass


class SeatsNotFoundError(BookingError):
    pass


class EventAnalyticsError(DomainError):
    pass


class EventNotFoundError(EventAnalyticsError):
    pass


class ForbiddenError(EventAnalyticsError):
    pass


class DashboardUnavailableError(EventAnalyticsError):
    pass


class EventError(DomainError):
    pass


class LockTimeoutError(EventError):
    pass
