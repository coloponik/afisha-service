from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from afisha.infrastracture.api_connectors.internal.payment import PaymentConnector
from afisha.infrastracture.api_connectors.internal.protection import ProtectionConnector
from tests.mock_connectors import MockPaymentConnector, MockProtectionConnector


class MockConnectorsProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_payment_connector(
        self,
    ) -> AsyncIterator[PaymentConnector]:
        connector = MockPaymentConnector()
        yield connector

    @provide(scope=Scope.APP)
    async def get_protection_connector(
        self,
    ) -> AsyncIterator[ProtectionConnector]:
        connector = MockProtectionConnector()
        yield connector
