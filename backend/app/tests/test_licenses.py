"""Unit tests for license calculation module."""

import pytest
from app.services.calculations.licenses import (
    calculate_licenses,
    calculate_license_cost,
    recommend_license_type,
)


class TestCalculateLicenses:
    """Test license calculation function."""

    def test_basic_license_calculation(self):
        """Test basic license calculation."""
        result = calculate_licenses(
            recorded_devices=50,
            live_only_devices=10,
        )
        
        # Only recorded devices need licenses
        assert result["licenses_required"] == 50
        assert result["recorded_devices"] == 50
        assert result["live_only_devices"] == 10

    def test_no_live_devices(self):
        """Test with no live-only devices."""
        result = calculate_licenses(
            recorded_devices=100,
            live_only_devices=0,
        )
        
        assert result["licenses_required"] == 100
        assert result["live_only_devices"] == 0

    def test_only_live_devices(self):
        """Test with only live-only devices (no licenses needed)."""
        result = calculate_licenses(
            recorded_devices=0,
            live_only_devices=50,
        )
        
        assert result["licenses_required"] == 0
        assert result["live_only_devices"] == 50

    def test_zero_devices(self):
        """Test with zero devices."""
        result = calculate_licenses(
            recorded_devices=0,
            live_only_devices=0,
        )
        
        assert result["licenses_required"] == 0

    def test_large_deployment(self):
        """Test with large deployment."""
        result = calculate_licenses(
            recorded_devices=2560,  # Max per site
            live_only_devices=100,
        )
        
        assert result["licenses_required"] == 2560


class TestCalculateLicenseCost:
    """Test license cost calculation."""

    def test_professional_license_cost(self):
        """Test Nx Professional license cost."""
        result = calculate_license_cost(
            num_licenses=50,
            license_type="professional",
            price_per_license=60.0,
        )
        
        # 50 × $60 = $3000
        assert result["total_cost"] == 3000.0
        assert result["license_type"] == "professional"
        assert result["num_licenses"] == 50

    def test_evos_service_cost(self):
        """Test Nx Evos service cost."""
        result = calculate_license_cost(
            num_licenses=100,
            license_type="evos",
            price_per_license=40.0,
        )
        
        # 100 × $40 = $4000
        assert result["total_cost"] == 4000.0
        assert result["license_type"] == "evos"

    def test_volume_discount(self):
        """Test volume discount application."""
        result = calculate_license_cost(
            num_licenses=500,
            license_type="professional",
            price_per_license=60.0,
            volume_discount=0.1,  # 10% discount
        )
        
        # 500 × $60 × 0.9 = $27,000
        assert result["total_cost"] == 27000.0
        assert result["discount_applied"] == 0.1

    def test_no_discount(self):
        """Test without volume discount."""
        result = calculate_license_cost(
            num_licenses=10,
            license_type="professional",
            price_per_license=60.0,
            volume_discount=0.0,
        )
        
        assert result["total_cost"] == 600.0
        assert result["discount_applied"] == 0.0

    def test_zero_licenses(self):
        """Test with zero licenses."""
        result = calculate_license_cost(
            num_licenses=0,
            license_type="professional",
            price_per_license=60.0,
        )
        
        assert result["total_cost"] == 0.0

    def test_fractional_price(self):
        """Test with fractional price per license."""
        result = calculate_license_cost(
            num_licenses=7,
            license_type="professional",
            price_per_license=59.99,
        )
        
        # 7 × $59.99 = $419.93
        assert abs(result["total_cost"] - 419.93) < 0.01


class TestRecommendLicenseType:
    """Test license type recommendation."""

    def test_recommend_professional_small(self):
        """Test recommendation for small deployment."""
        result = recommend_license_type(
            num_devices=10,
            use_case="security",
        )
        
        assert result["recommended_type"] in ["professional", "evos"]

    def test_recommend_professional_large(self):
        """Test recommendation for large deployment."""
        result = recommend_license_type(
            num_devices=500,
            use_case="enterprise",
        )
        
        assert result["recommended_type"] == "professional"

    def test_recommend_evos_cloud(self):
        """Test recommendation for cloud use case."""
        result = recommend_license_type(
            num_devices=50,
            use_case="cloud",
        )
        
        # Evos is cloud-based service
        assert result["recommended_type"] == "evos"

    def test_recommendation_includes_reasoning(self):
        """Test recommendation includes reasoning."""
        result = recommend_license_type(
            num_devices=100,
            use_case="security",
        )
        
        assert "reasoning" in result
        assert len(result["reasoning"]) > 0

    def test_recommendation_includes_alternatives(self):
        """Test recommendation includes alternatives."""
        result = recommend_license_type(
            num_devices=50,
            use_case="security",
        )
        
        assert "alternatives" in result


class TestLicenseEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_negative_devices(self):
        """Test with negative device count."""
        with pytest.raises(ValueError, match="Number of devices cannot be negative"):
            calculate_licenses(
                recorded_devices=-1,
                live_only_devices=0,
            )

    def test_negative_price(self):
        """Test with negative price."""
        with pytest.raises(ValueError, match="Price per license must be positive"):
            calculate_license_cost(
                num_licenses=10,
                license_type="professional",
                price_per_license=-60.0,
            )

    def test_invalid_discount(self):
        """Test with invalid discount (> 100%)."""
        with pytest.raises(ValueError, match="Discount must be between 0 and 1"):
            calculate_license_cost(
                num_licenses=10,
                license_type="professional",
                price_per_license=60.0,
                volume_discount=1.5,  # 150% discount invalid
            )

    def test_max_devices_per_site(self):
        """Test with maximum devices per site."""
        result = calculate_licenses(
            recorded_devices=2560,
            live_only_devices=0,
        )
        
        assert result["licenses_required"] == 2560

    def test_single_device(self):
        """Test with single device."""
        result = calculate_licenses(
            recorded_devices=1,
            live_only_devices=0,
        )
        
        assert result["licenses_required"] == 1

    def test_mixed_device_types(self):
        """Test with mix of recorded and live-only devices."""
        result = calculate_licenses(
            recorded_devices=75,
            live_only_devices=25,
        )
        
        # Total 100 devices, but only 75 need licenses
        assert result["licenses_required"] == 75
        assert result["total_devices"] == 100


class TestLicenseBreakdown:
    """Test license breakdown and details."""

    def test_license_breakdown_by_type(self):
        """Test license breakdown by device type."""
        result = calculate_licenses(
            recorded_devices=100,
            live_only_devices=20,
            device_breakdown={
                "cameras": 80,
                "encoders": 20,
                "io_modules": 20,
            },
        )
        
        assert result["licenses_required"] == 100
        assert "device_breakdown" in result

    def test_license_cost_breakdown(self):
        """Test license cost includes breakdown."""
        result = calculate_license_cost(
            num_licenses=100,
            license_type="professional",
            price_per_license=60.0,
            volume_discount=0.15,
        )
        
        # Should include subtotal, discount amount, and total
        assert "subtotal" in result
        assert "discount_amount" in result
        assert result["subtotal"] == 6000.0
        assert result["discount_amount"] == 900.0
        assert result["total_cost"] == 5100.0


# Property-based tests
try:
    from hypothesis import given, strategies as st

    class TestLicenseProperties:
        """Property-based tests for license calculations."""

        @given(
            recorded=st.integers(min_value=0, max_value=2560),
            live_only=st.integers(min_value=0, max_value=500),
        )
        def test_licenses_never_exceed_recorded(self, recorded, live_only):
            """Licenses required should never exceed recorded devices."""
            result = calculate_licenses(recorded, live_only)
            assert result["licenses_required"] == recorded
            assert result["licenses_required"] <= result["total_devices"]

        @given(
            licenses=st.integers(min_value=1, max_value=1000),
            price=st.floats(min_value=1.0, max_value=1000.0),
        )
        def test_cost_scales_linearly(self, licenses, price):
            """Cost should scale linearly with license count."""
            result = calculate_license_cost(licenses, "professional", price, 0.0)
            expected = licenses * price
            assert abs(result["total_cost"] - expected) < 0.01

except ImportError:
    # Hypothesis not installed
    pass

