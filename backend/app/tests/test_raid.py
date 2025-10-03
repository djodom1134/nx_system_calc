"""Unit tests for RAID calculation module."""

import pytest
from app.services.calculations.raid import (
    calculate_raid_capacity,
    calculate_usable_storage,
    get_raid_efficiency,
    recommend_raid_level,
)


class TestCalculateRAIDCapacity:
    """Test RAID capacity calculation."""

    def test_raid_0(self):
        """Test RAID 0 (striping, no redundancy)."""
        result = calculate_raid_capacity(
            raid_level="raid_0",
            num_drives=4,
            drive_capacity_tb=2,
        )
        
        # RAID 0: All drives usable
        # 4 × 2TB = 8TB
        assert result["usable_capacity_tb"] == 8.0
        assert result["efficiency_percent"] == 100.0
        assert result["redundancy_level"] == 0

    def test_raid_1(self):
        """Test RAID 1 (mirroring)."""
        result = calculate_raid_capacity(
            raid_level="raid_1",
            num_drives=2,
            drive_capacity_tb=2,
        )
        
        # RAID 1: 50% efficiency (mirroring)
        # 2 × 2TB = 4TB raw, 2TB usable
        assert result["usable_capacity_tb"] == 2.0
        assert result["efficiency_percent"] == 50.0
        assert result["redundancy_level"] == 1

    def test_raid_5(self):
        """Test RAID 5 (striping with parity)."""
        result = calculate_raid_capacity(
            raid_level="raid_5",
            num_drives=4,
            drive_capacity_tb=2,
        )
        
        # RAID 5: (n-1) drives usable
        # 4 × 2TB = 8TB raw, 6TB usable (75% efficiency)
        assert result["usable_capacity_tb"] == 6.0
        assert result["efficiency_percent"] == 75.0
        assert result["redundancy_level"] == 1

    def test_raid_6(self):
        """Test RAID 6 (double parity)."""
        result = calculate_raid_capacity(
            raid_level="raid_6",
            num_drives=6,
            drive_capacity_tb=2,
        )
        
        # RAID 6: (n-2) drives usable
        # 6 × 2TB = 12TB raw, 8TB usable (66.67% efficiency)
        assert result["usable_capacity_tb"] == 8.0
        assert abs(result["efficiency_percent"] - 66.67) < 0.1
        assert result["redundancy_level"] == 2

    def test_raid_10(self):
        """Test RAID 10 (mirrored striping)."""
        result = calculate_raid_capacity(
            raid_level="raid_10",
            num_drives=4,
            drive_capacity_tb=2,
        )
        
        # RAID 10: 50% efficiency (mirroring)
        # 4 × 2TB = 8TB raw, 4TB usable
        assert result["usable_capacity_tb"] == 4.0
        assert result["efficiency_percent"] == 50.0
        assert result["redundancy_level"] == 1

    def test_invalid_raid_level(self):
        """Test with invalid RAID level."""
        with pytest.raises(ValueError, match="Invalid RAID level"):
            calculate_raid_capacity(
                raid_level="raid_99",
                num_drives=4,
                drive_capacity_tb=2,
            )

    def test_insufficient_drives_raid_5(self):
        """Test RAID 5 requires minimum 3 drives."""
        with pytest.raises(ValueError, match="RAID 5 requires at least 3 drives"):
            calculate_raid_capacity(
                raid_level="raid_5",
                num_drives=2,
                drive_capacity_tb=2,
            )

    def test_insufficient_drives_raid_6(self):
        """Test RAID 6 requires minimum 4 drives."""
        with pytest.raises(ValueError, match="RAID 6 requires at least 4 drives"):
            calculate_raid_capacity(
                raid_level="raid_6",
                num_drives=3,
                drive_capacity_tb=2,
            )

    def test_insufficient_drives_raid_10(self):
        """Test RAID 10 requires minimum 4 drives."""
        with pytest.raises(ValueError, match="RAID 10 requires at least 4 drives"):
            calculate_raid_capacity(
                raid_level="raid_10",
                num_drives=2,
                drive_capacity_tb=2,
            )


class TestCalculateUsableStorage:
    """Test usable storage calculation."""

    def test_usable_storage_with_overhead(self):
        """Test usable storage accounts for filesystem overhead."""
        result = calculate_usable_storage(
            raw_capacity_tb=10.0,
            raid_level="raid_5",
            num_drives=5,
            filesystem_overhead=0.05,  # 5% overhead
        )
        
        # RAID 5 with 5 drives: 4/5 = 80% efficiency
        # 10TB × 0.8 = 8TB after RAID
        # 8TB × 0.95 = 7.6TB after filesystem overhead
        assert abs(result["usable_capacity_tb"] - 7.6) < 0.1

    def test_usable_storage_no_overhead(self):
        """Test usable storage without filesystem overhead."""
        result = calculate_usable_storage(
            raw_capacity_tb=10.0,
            raid_level="raid_0",
            num_drives=5,
            filesystem_overhead=0.0,
        )
        
        # RAID 0: 100% efficiency, no overhead
        assert result["usable_capacity_tb"] == 10.0

    def test_usable_storage_breakdown(self):
        """Test usable storage includes breakdown."""
        result = calculate_usable_storage(
            raw_capacity_tb=12.0,
            raid_level="raid_6",
            num_drives=6,
            filesystem_overhead=0.1,  # 10% overhead
        )
        
        # RAID 6 with 6 drives: 4/6 = 66.67% efficiency
        # 12TB × 0.6667 = 8TB after RAID
        # 8TB × 0.9 = 7.2TB after filesystem overhead
        assert "raid_overhead_tb" in result
        assert "filesystem_overhead_tb" in result
        assert abs(result["usable_capacity_tb"] - 7.2) < 0.1


class TestGetRAIDEfficiency:
    """Test RAID efficiency lookup."""

    def test_raid_0_efficiency(self):
        """Test RAID 0 efficiency is 100%."""
        efficiency = get_raid_efficiency("raid_0", 4)
        assert efficiency == 1.0

    def test_raid_1_efficiency(self):
        """Test RAID 1 efficiency is 50%."""
        efficiency = get_raid_efficiency("raid_1", 2)
        assert efficiency == 0.5

    def test_raid_5_efficiency(self):
        """Test RAID 5 efficiency varies with drive count."""
        # 3 drives: 2/3 = 66.67%
        assert abs(get_raid_efficiency("raid_5", 3) - 0.6667) < 0.01
        
        # 4 drives: 3/4 = 75%
        assert get_raid_efficiency("raid_5", 4) == 0.75
        
        # 5 drives: 4/5 = 80%
        assert get_raid_efficiency("raid_5", 5) == 0.8

    def test_raid_6_efficiency(self):
        """Test RAID 6 efficiency varies with drive count."""
        # 4 drives: 2/4 = 50%
        assert get_raid_efficiency("raid_6", 4) == 0.5
        
        # 6 drives: 4/6 = 66.67%
        assert abs(get_raid_efficiency("raid_6", 6) - 0.6667) < 0.01
        
        # 8 drives: 6/8 = 75%
        assert get_raid_efficiency("raid_6", 8) == 0.75

    def test_raid_10_efficiency(self):
        """Test RAID 10 efficiency is 50%."""
        efficiency = get_raid_efficiency("raid_10", 4)
        assert efficiency == 0.5


class TestRecommendRAIDLevel:
    """Test RAID level recommendation."""

    def test_recommend_for_small_deployment(self):
        """Test recommendation for small deployment."""
        result = recommend_raid_level(
            num_drives=2,
            priority="performance",
        )
        
        # With 2 drives, only RAID 0 or RAID 1 possible
        assert result["recommended_raid"] in ["raid_0", "raid_1"]

    def test_recommend_for_redundancy(self):
        """Test recommendation prioritizing redundancy."""
        result = recommend_raid_level(
            num_drives=6,
            priority="redundancy",
        )
        
        # Should recommend RAID 6 for maximum redundancy
        assert result["recommended_raid"] == "raid_6"

    def test_recommend_for_performance(self):
        """Test recommendation prioritizing performance."""
        result = recommend_raid_level(
            num_drives=4,
            priority="performance",
        )
        
        # Should recommend RAID 0 or RAID 10 for performance
        assert result["recommended_raid"] in ["raid_0", "raid_10"]

    def test_recommend_for_balanced(self):
        """Test recommendation for balanced approach."""
        result = recommend_raid_level(
            num_drives=5,
            priority="balanced",
        )
        
        # Should recommend RAID 5 for balance
        assert result["recommended_raid"] == "raid_5"

    def test_recommendation_includes_alternatives(self):
        """Test recommendation includes alternatives."""
        result = recommend_raid_level(
            num_drives=6,
            priority="balanced",
        )
        
        assert "alternatives" in result
        assert len(result["alternatives"]) > 0


class TestRAIDEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_drive(self):
        """Test with single drive (no RAID)."""
        result = calculate_raid_capacity(
            raid_level="raid_0",
            num_drives=1,
            drive_capacity_tb=2,
        )
        
        assert result["usable_capacity_tb"] == 2.0

    def test_large_drive_count(self):
        """Test with many drives."""
        result = calculate_raid_capacity(
            raid_level="raid_5",
            num_drives=12,
            drive_capacity_tb=4,
        )
        
        # RAID 5 with 12 drives: 11/12 = 91.67% efficiency
        # 12 × 4TB = 48TB raw, 44TB usable
        assert result["usable_capacity_tb"] == 44.0

    def test_fractional_capacity(self):
        """Test with fractional drive capacity."""
        result = calculate_raid_capacity(
            raid_level="raid_1",
            num_drives=2,
            drive_capacity_tb=1.5,
        )
        
        # RAID 1: 50% efficiency
        # 2 × 1.5TB = 3TB raw, 1.5TB usable
        assert result["usable_capacity_tb"] == 1.5

    def test_zero_capacity(self):
        """Test with zero capacity."""
        with pytest.raises(ValueError, match="Drive capacity must be positive"):
            calculate_raid_capacity(
                raid_level="raid_0",
                num_drives=4,
                drive_capacity_tb=0,
            )

    def test_negative_drives(self):
        """Test with negative drive count."""
        with pytest.raises(ValueError, match="Number of drives must be positive"):
            calculate_raid_capacity(
                raid_level="raid_0",
                num_drives=-1,
                drive_capacity_tb=2,
            )

