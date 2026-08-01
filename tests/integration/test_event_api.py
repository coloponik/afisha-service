import pytest
from dishka import Scope
from sqlalchemy import select

from afisha.infrastracture.postgres.manager import DatabaseManager
from afisha.infrastracture.postgres.models import Booking, BookingStatus, EventSeat, SeatStatus


class TestPrepareCheckout:
    @pytest.mark.parametrize(
        "test_event_id, test_headers, test_json",
        [
            (1, {'x-user-id': "1"}, {"seat_ids": [2]})
        ]
    )
    async def test_returns_booking_data(
            self,
            async_client,
            test_event_id: int,
            test_headers: dict,
            test_json: dict
    ) -> None:
        response = await async_client.post(
            f"/events/{test_event_id}/checkout",
            headers=test_headers,
            json=test_json,
        )
        body = response.json()

        assert response.status_code == 200
        assert "booking" in body
        assert "payment" in body
        assert "protection" in body

    @pytest.mark.parametrize(
        "test_event_id, test_headers, test_json",
        [
            (1, {'x-user-id': "1"}, {"seat_ids": [2]})
        ]
    )
    async def test_rejects_already_reserved_seats(
            self,
            async_client,
            test_event_id: int,
            test_headers: dict,
            test_json: dict
    ) -> None:
        response = await async_client.post(
            f"/events/{test_event_id}/checkout",
            headers=test_headers,
            json=test_json
        )

        assert response.status_code == 200

        response = await async_client.post(
            f"/events/{test_event_id}/checkout",
            headers=test_headers,
            json=test_json
        )

        assert response.status_code == 409

    @pytest.mark.parametrize(
        "test_event_id, test_headers, test_json",
        [
            (1, {'x-user-id': "1"}, {"seat_ids": [2]})
        ]
    )
    async def test_prepare_checkout_creates_booking_and_reserves_seats(
            self,
            async_client,
            test_container,
            test_event_id: int,
            test_headers: dict,
            test_json: dict
    ):
        response = await async_client.post(
            f"/events/{test_event_id}/checkout",
            headers=test_headers,
            json=test_json,
        )

        assert response.status_code == 200

        async with test_container(scope=Scope.REQUEST) as container:
            db = await container.get(DatabaseManager)

            booking = await db.session.scalar(
                select(Booking)
                .where(Booking.id == 2)
            )

            assert booking is not None
            assert booking.status == BookingStatus.pending_payment

            event_seat = await db.session.scalar(
                select(EventSeat)
                .where(EventSeat.seat_id == 2)
            )

            assert event_seat.status == SeatStatus.reserved
            assert event_seat.booking_id == booking.id
