from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from afisha.core.config import PostgresConfig, ConnectorsConfig


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    def get_postgres(self, config: PostgresConfig) -> AsyncIterator:
        pass

    @provide(scope=Scope.REQUEST)
    def get_db(self) -> AsyncIterator:
        pass


class ConnectorsProvider(Provider):
    @provide(scope=Scope.APP)
    def get_payment_connector(self, config: ConnectorsConfig) -> AsyncIterator:
        pass

    @provide(scope=Scope.APP)
    def get_protection_connector(self, config: ConnectorsConfig) -> AsyncIterator:
        pass
