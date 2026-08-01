import httpx
import pytest


class TestGetEventDashboard:
    @pytest.mark.parametrize(
        "test_event_id, test_headers",
        [
            (1, {"x-user-id": "1"})
        ]
    )
    async def test_returns_event_dashboard(
            self,
            async_client: httpx.AsyncClient,
            test_event_id: int,
            test_headers: dict
    ) -> None:

        first_response = await async_client.post(
                f"/events/{test_event_id}/checkout",
                headers=test_headers,
                json={"seat_ids": [2, 3]},
        )

        assert first_response.status_code == 200

        second_response = await async_client.get(
            f"/organizer/events/{test_event_id}/dashboard",
            headers=test_headers,

        )
        body = second_response.json()

        assert second_response.status_code == 200

        assert "event_title" in body
        assert "starts_at" in body
        assert body["sales"]["paid_orders"] == 1
        assert body["sales"]["sold_tickets"] == 1
        assert body["sales"]["average_order"] == 1000
        assert body["occupancy"]["reserved"] == 2
        assert body["occupancy"]["occupancy_percent"] == 6

    @pytest.mark.parametrize(
        "test_event_id, test_headers",
        [
            (1, {"x-user-id": "999"})
        ]
    )
    async def test_forbidden_for_other_users(
            self,
            async_client: httpx.AsyncClient,
            test_event_id: int,
            test_headers: dict
    ) -> None:
        response = await async_client.get(
            f"/organizer/events/{test_event_id}/dashboard",
            headers=test_headers,

        )

        assert response.status_code == 403
