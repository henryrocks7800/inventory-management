"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockRecommendations:
    """Test suite for restock recommendation endpoint."""

    def test_recommendations_requires_budget(self, client):
        """Test that budget is a required query parameter."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 422

    def test_recommendations_zero_budget(self, client):
        """Test that a zero budget yields no recommendations."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["recommendations"] == []
        assert data["total_estimated_cost"] == 0
        assert data["remaining_budget"] == 0

    def test_recommendations_structure(self, client):
        """Test that recommendations have the expected fields and types."""
        response = client.get("/api/restocking/recommendations?budget=1000000")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0

        for rec in data["recommendations"]:
            assert "item_sku" in rec
            assert "item_name" in rec
            assert "current_demand" in rec
            assert "forecasted_demand" in rec
            assert "demand_gap" in rec
            assert "unit_cost" in rec
            assert "recommended_quantity" in rec
            assert "line_total" in rec
            assert "fits_budget" in rec
            assert isinstance(rec["recommended_quantity"], int)
            assert isinstance(rec["fits_budget"], bool)

    def test_recommendations_sorted_by_demand_gap_desc(self, client):
        """Test that recommendations are prioritized by demand gap, largest first."""
        response = client.get("/api/restocking/recommendations?budget=1000000")
        data = response.json()

        gaps = [rec["demand_gap"] for rec in data["recommendations"]]
        assert gaps == sorted(gaps, reverse=True)

    def test_recommendations_exclude_non_positive_gap(self, client):
        """Test that items with no shortfall are never recommended."""
        response = client.get("/api/restocking/recommendations?budget=1000000")
        data = response.json()

        for rec in data["recommendations"]:
            assert rec["demand_gap"] > 0

    def test_recommendations_respect_budget(self, client):
        """Test that recommended spend never exceeds the given budget."""
        for budget in (500, 5000, 50000):
            response = client.get(f"/api/restocking/recommendations?budget={budget}")
            data = response.json()

            total_line_cost = sum(rec["line_total"] for rec in data["recommendations"])
            assert total_line_cost <= budget + 0.01
            assert data["total_estimated_cost"] <= budget + 0.01

    def test_low_budget_yields_fewer_recommendations_than_high_budget(self, client):
        """Test that a smaller budget results in fewer or equal recommended items."""
        low_response = client.get("/api/restocking/recommendations?budget=100")
        high_response = client.get("/api/restocking/recommendations?budget=1000000")

        low_data = low_response.json()
        high_data = high_response.json()

        assert len(low_data["recommendations"]) <= len(high_data["recommendations"])


class TestRestockOrderCreation:
    """Test suite for restock order creation endpoint."""

    def test_create_restock_order_success(self, client):
        """Test creating a restock order with valid line items."""
        payload = {
            "line_items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 10,
                    "unit_cost": 5.0,
                    "line_total": 50.0
                }
            ]
        }
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"].startswith("RSO-")
        assert order["status"] == "Pending"
        assert order["lead_time_days"] == 14
        assert order["total_cost"] == 50.0
        assert len(order["line_items"]) == 1

    def test_create_restock_order_computes_total_cost_server_side(self, client):
        """Test that total_cost and line_total are recomputed, not trusted from the client."""
        payload = {
            "line_items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 4,
                    "unit_cost": 10.0,
                    "line_total": 999.0  # deliberately wrong
                }
            ]
        }
        response = client.post("/api/restocking/orders", json=payload)
        order = response.json()

        assert order["line_items"][0]["line_total"] == 40.0
        assert order["total_cost"] == 40.0

    def test_create_restock_order_expected_delivery_after_created_date(self, client):
        """Test that expected_delivery is later than created_date by the lead time."""
        payload = {
            "line_items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 1,
                    "unit_cost": 5.0,
                    "line_total": 5.0
                }
            ]
        }
        response = client.post("/api/restocking/orders", json=payload)
        order = response.json()

        assert order["expected_delivery"] > order["created_date"]

    def test_create_restock_order_empty_line_items_rejected(self, client):
        """Test that an order with no line items is rejected."""
        response = client.post("/api/restocking/orders", json={"line_items": []})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data


class TestRestockOrdersRetrieval:
    """Test suite for retrieving submitted restock orders."""

    def test_created_order_appears_in_list(self, client):
        """Test that a newly created order shows up in the GET list."""
        before_response = client.get("/api/restocking/orders")
        before_count = len(before_response.json())

        payload = {
            "line_items": [
                {
                    "item_sku": "BRG-102",
                    "item_name": "Steel Bearing Assembly",
                    "quantity": 5,
                    "unit_cost": 8.0,
                    "line_total": 40.0
                }
            ]
        }
        create_response = client.post("/api/restocking/orders", json=payload)
        created_order_number = create_response.json()["order_number"]

        after_response = client.get("/api/restocking/orders")
        after_data = after_response.json()

        assert len(after_data) == before_count + 1
        assert any(o["order_number"] == created_order_number for o in after_data)
