from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from afisha.core.config import PostgresConfig, ConnectorsConfig
from afisha.infrastracture.api_connectors.internal.payment import PaymentConnector
from afisha.infrastracture.api_connectors.internal.protection import ProtectionConnector
from afisha.infrastracture.postgres.manager import PostgresClient, DatabaseManager


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_postgres(self, config: PostgresConfig) -> AsyncIterator[PostgresClient]:
        postgres = PostgresClient(config)

        yield postgres

        await postgres.close()

    @provide(scope=Scope.REQUEST)
    async def get_db(self, postgres: PostgresClient) -> AsyncIterator[DatabaseManager]:
        async with postgres.session() as db:
            yield db


class ConnectorsProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_payment_connector(
            self,
            config: ConnectorsConfig
    ) -> AsyncIterator[PaymentConnector]:
        payment_config = config.payment
        connector = PaymentConnector(
            base_url=payment_config.base_url,
            timeout=payment_config.timeout,
            rate_limit_requests=payment_config.rate_limit_requests,
            rate_limit_interval=payment_config.rate_limit_interval
        )

        yield connector

        await connector.close_clint()

    @provide(scope=Scope.APP)
    async def get_protection_connector(
            self,
            config: ConnectorsConfig
    ) -> AsyncIterator[ProtectionConnector]:
        protection_config = config.protection
        connector = ProtectionConnector(
            base_url=protection_config.base_url,
            timeout=protection_config.timeout,
            rate_limit_requests=protection_config.rate_limit_requests,
            rate_limit_interval=protection_config.rate_limit_interval
        )

        yield connector

        await connector.close_clint()
