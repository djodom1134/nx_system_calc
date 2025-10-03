"""Chart generation for PDF reports using matplotlib."""

import io
from typing import Dict, Any, Optional, List
import tempfile
import os

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.figure import Figure
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ChartGenerator:
    """Generate charts for PDF reports using matplotlib."""

    # Color scheme matching the PDF theme
    COLORS = {
        'primary': '#2563eb',
        'secondary': '#3b82f6',
        'accent': '#60a5fa',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'gray': '#6b7280',
        'light_gray': '#e5e7eb',
    }

    def __init__(self):
        """Initialize chart generator."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for chart generation. Install with: pip install matplotlib")

        # Set default style
        plt.style.use('seaborn-v0_8-darkgrid')

    def generate_storage_breakdown_chart(
        self,
        storage_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate pie chart showing storage breakdown.

        Args:
            storage_data: Storage calculation results
            output_path: Optional path to save chart

        Returns:
            Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Extract data
        usable_storage = storage_data.get('total_storage_gb', 0)
        raid_overhead = storage_data.get('raid_overhead_gb', 0)

        # Handle zero storage case
        if usable_storage == 0 and raid_overhead == 0:
            # Create a simple text message instead of pie chart
            ax.text(0.5, 0.5, 'No Storage Data Available',
                   ha='center', va='center', fontsize=16, fontweight='bold')
            ax.axis('off')
        else:
            # Create pie chart
            sizes = [usable_storage, raid_overhead]
            labels = ['Usable Storage', 'RAID Overhead']
            colors = [self.COLORS['primary'], self.COLORS['light_gray']]
            explode = (0.05, 0)  # Explode the usable storage slice

            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')

        plt.title('Storage Breakdown', fontsize=16, fontweight='bold', pad=20)

        # Save to file
        if not output_path:
            output_path = tempfile.mktemp(suffix='.png')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_bitrate_distribution_chart(
        self,
        camera_groups: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate bar chart showing bitrate distribution across camera groups.

        Args:
            camera_groups: List of camera group configurations
            output_path: Optional path to save chart

        Returns:
            Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        group_names = []
        bitrates = []

        for i, group in enumerate(camera_groups):
            resolution = group.get('resolution_id', 'Unknown')
            num_cameras = group.get('num_cameras', 0)
            bitrate_per_camera = group.get('bitrate_kbps', 0) / 1000  # Convert to Mbps
            total_bitrate = bitrate_per_camera * num_cameras

            group_names.append(f"{resolution}\n({num_cameras} cams)")
            bitrates.append(total_bitrate)

        # Create bar chart
        x_pos = np.arange(len(group_names))
        bars = ax.bar(x_pos, bitrates, color=self.COLORS['primary'], alpha=0.8)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=10)

        ax.set_xlabel('Camera Groups', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Bitrate (Mbps)', fontsize=12, fontweight='bold')
        ax.set_title('Bitrate Distribution by Camera Group', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(group_names, fontsize=9)
        ax.grid(axis='y', alpha=0.3)

        # Save to file
        if not output_path:
            output_path = tempfile.mktemp(suffix='.png')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_server_capacity_chart(
        self,
        server_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate bar chart showing server capacity utilization.

        Args:
            server_data: Server calculation results
            output_path: Optional path to save chart

        Returns:
            Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        devices_per_server = server_data.get('devices_per_server', 0)
        max_devices = 256  # Max devices per server

        bitrate_per_server = server_data.get('bitrate_per_server_mbps', 0)
        max_bitrate = 1000  # Max bitrate per server (Mbps)

        # Create grouped bar chart
        categories = ['Device Capacity', 'Bitrate Capacity']
        current_values = [devices_per_server, bitrate_per_server]
        max_values = [max_devices, max_bitrate]

        x_pos = np.arange(len(categories))
        width = 0.35

        bars1 = ax.bar(x_pos - width/2, current_values, width,
                      label='Current', color=self.COLORS['primary'], alpha=0.8)
        bars2 = ax.bar(x_pos + width/2, max_values, width,
                      label='Maximum', color=self.COLORS['light_gray'], alpha=0.8)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=10)

        ax.set_ylabel('Capacity', fontsize=12, fontweight='bold')
        ax.set_title('Server Capacity Utilization', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        # Save to file
        if not output_path:
            output_path = tempfile.mktemp(suffix='.png')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_storage_timeline_chart(
        self,
        storage_data: Dict[str, Any],
        retention_days: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate line chart showing storage accumulation over retention period.

        Args:
            storage_data: Storage calculation results
            retention_days: Retention period in days
            output_path: Optional path to save chart

        Returns:
            Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate daily storage
        total_storage_gb = storage_data.get('total_storage_gb', 0)
        daily_storage_gb = storage_data.get('daily_storage_gb', 0)

        # Generate timeline data
        days = np.arange(0, retention_days + 1)
        storage_accumulated = days * daily_storage_gb

        # Cap at total storage
        storage_accumulated = np.minimum(storage_accumulated, total_storage_gb)

        # Create line chart
        ax.plot(days, storage_accumulated, color=self.COLORS['primary'],
               linewidth=2.5, marker='o', markersize=4, markevery=max(1, retention_days // 10))

        # Add horizontal line for total capacity
        ax.axhline(y=total_storage_gb, color=self.COLORS['danger'],
                  linestyle='--', linewidth=2, label=f'Total Capacity ({total_storage_gb:.0f} GB)')

        # Fill area under curve
        ax.fill_between(days, storage_accumulated, alpha=0.3, color=self.COLORS['primary'])

        ax.set_xlabel('Days', fontsize=12, fontweight='bold')
        ax.set_ylabel('Storage (GB)', fontsize=12, fontweight='bold')
        ax.set_title('Storage Accumulation Over Time', fontsize=16, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Save to file
        if not output_path:
            output_path = tempfile.mktemp(suffix='.png')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def generate_codec_comparison_chart(
        self,
        codec_data: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate bar chart comparing different codecs.

        Args:
            codec_data: List of codec comparison data
            output_path: Optional path to save chart

        Returns:
            Path to generated chart image
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        codec_names = [item.get('codec', 'Unknown') for item in codec_data]
        bitrates = [item.get('bitrate_mbps', 0) for item in codec_data]
        storage = [item.get('storage_tb', 0) for item in codec_data]

        # Create grouped bar chart
        x_pos = np.arange(len(codec_names))
        width = 0.35

        # Normalize for comparison
        max_bitrate = max(bitrates) if bitrates else 1
        max_storage = max(storage) if storage else 1

        bars1 = ax.bar(x_pos - width/2, bitrates, width,
                      label='Bitrate (Mbps)', color=self.COLORS['primary'], alpha=0.8)

        # Create second y-axis for storage
        ax2 = ax.twinx()
        bars2 = ax2.bar(x_pos + width/2, storage, width,
                       label='Storage (TB)', color=self.COLORS['secondary'], alpha=0.8)

        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)

        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Codec', fontsize=12, fontweight='bold')
        ax.set_ylabel('Bitrate (Mbps)', fontsize=12, fontweight='bold', color=self.COLORS['primary'])
        ax2.set_ylabel('Storage (TB)', fontsize=12, fontweight='bold', color=self.COLORS['secondary'])
        ax.set_title('Codec Comparison', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(codec_names, fontsize=11)

        # Combine legends
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)

        ax.grid(axis='y', alpha=0.3)

        # Save to file
        if not output_path:
            output_path = tempfile.mktemp(suffix='.png')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

