from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, \
    async_sessionmaker

from afisha.core.config import PostgresConfig
from afisha.infrastracture.postgres.repositories.bookings import BookingRepo
from afisha.infrastracture.postgres.repositories.event_seats import EventSeatRepo
from afisha.infrastracture.postgres.repositories.events import EventRepo
from afisha.infrastracture.postgres.repositories.seats import SeatRepo


class PostgresClient:
    def __init__(self, config: PostgresConfig):
        self._engine: AsyncEngine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=True
        )

        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False
        )

    @asynccontextmanager
    async def session(self):
        async with self._session_maker() as session:
            db = DatabaseManager(session, self._session_maker)
            try:

                yield db
            except Exception:
                await db.rollback()
                raise
    @property
    def session_maker(self):
        return self._session_maker

    async def close(self):
        await self._engine.dispose()


class DatabaseManager:
    def __init__(self, session: AsyncSession, session_maker: async_sessionmaker) -> None:
        self.session = session
        self.session_maker = session_maker

    @asynccontextmanager
    async def transaction(self):
        async with self.session_maker() as new_session:
            db = DatabaseManager(new_session, self.session_maker)
            try:
                yield db
                await db.commit()
            except Exception:
                await db.rollback()
                raise

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    @property
    def bookings(self) -> BookingRepo:
        return BookingRepo(self.session)

    @property
    def event_seats(self) -> EventSeatRepo:
        return EventSeatRepo(self.session)

    @property
    def events(self) -> EventRepo:
        return EventRepo(self.session)

    @property
    def seats(self) -> SeatRepo:
        return SeatRepo(self.session)

