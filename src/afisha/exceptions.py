
class DomainError(Exception):
    pass


class InfrastructureError(Exception):
    pass


class BookingError(DomainError):
    pass


class EventError(DomainError):
    pass


class EventAnalyticsError(DomainError):
    pass


class PaymentUnavailableError(BookingError):
    pass


class SeatAlreadyReservedError(BookingError):
    pass


class SeatAlreadySoldError(BookingError):
    pass


class SeatsNotFoundError(BookingError):
    pass


class LockTimeoutError(EventError):
    pass


class DashboardUnavailableError(EventAnalyticsError):
    pass


class EventNotFoundError(EventAnalyticsError):
    pass


class ForbiddenError(EventAnalyticsError):
    pass


class PostgresEventQueueError(InfrastructureError):
    pass


class EventViewPersistenceError(PostgresEventQueueError):
    pass
