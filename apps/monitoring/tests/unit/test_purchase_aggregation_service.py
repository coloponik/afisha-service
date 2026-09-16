from monitoring.services.purchase_aggregation import PurchaseAggregationService


class TestPurchaseAggregationService:
    def test_aggregate_events_groups_events(
            self,
            purchase_aggregation_service: PurchaseAggregationService,
            fake_events: list[dict]
    ) -> None:

        result = purchase_aggregation_service._aggregate_events(fake_events)

        assert len(result) == 2

        event_1 = next(
            aggregate
            for aggregate in result
            if aggregate["event_id"] == 1
        )
        event_2 = next(
            aggregate
            for aggregate in result
            if aggregate["event_id"] == 2
        )

        assert event_1["payments_count"] == 2
        assert event_1["tickets_count"] == 5
        assert event_1["total_amount"] == 5500

        assert event_2["payments_count"] == 1
        assert event_2["tickets_count"] == 1
        assert event_2["total_amount"] == 1000

        assert event_1["batch_id"] == event_2["batch_id"]
