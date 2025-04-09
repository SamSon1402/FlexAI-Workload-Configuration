import unittest
import sys
import os
import plotly.graph_objects as go

# Add the parent directory to the path so we can import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualizations import (
    create_cost_time_comparison,
    create_resource_comparison_chart
)

class TestVisualizations(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create a sample recommendation
        self.recommendation = {
            "gpu_type": "NVIDIA A100",
            "gpu_count": 2,
            "instance_type": "flex-standard",
            "region": "us-east",
            "estimated_cost": 5.78,
            "estimated_time": "3.5 hours",
            "justification": ["Test justification"],
            "alternatives": []
        }
        
        # Create sample alternatives
        self.alternatives = [
            {
                "name": "Budget Option",
                "gpu_type": "NVIDIA T4",
                "gpu_count": 2,
                "instance_type": "flex-economy",
                "region": "us-east",
                "estimated_cost": 0.91,
                "description": "A more cost-effective configuration saving 84% on hourly costs."
            },
            {
                "name": "Performance Option",
                "gpu_type": "NVIDIA H100",
                "gpu_count": 2,
                "instance_type": "flex-performance",
                "region": "us-east",
                "estimated_cost": 16.13,
                "description": "A higher-performance configuration for faster results."
            }
        ]
        
        # Update recommendation with alternatives
        self.recommendation["alternatives"] = self.alternatives
    
    def test_create_cost_time_comparison(self):
        """Test creating a cost vs time comparison chart"""
        # Test with recommendation and alternatives
        fig = create_cost_time_comparison(self.recommendation, self.alternatives)
        
        # Should return a valid figure
        self.assertIsInstance(fig, go.Figure)
        
        # Should have 3 data points (recommendation + 2 alternatives)
        self.assertEqual(len(fig.data), 3)
        
        # Test with real-time inference (should return None)
        realtime_rec = self.recommendation.copy()
        realtime_rec["estimated_time"] = "Low latency (ms)"
        
        fig = create_cost_time_comparison(realtime_rec, self.alternatives)
        self.assertIsNone(fig)
    
    def test_create_resource_comparison_chart(self):
        """Test creating a resource comparison chart"""
        # Test with recommendation and alternatives
        fig = create_resource_comparison_chart(self.recommendation, self.alternatives)
        
        # Should return a valid figure
        self.assertIsInstance(fig, go.Figure)
        
        # Should have 9 traces (3 resource types x 3 configurations)
        self.assertEqual(len(fig.data), 3)
        
        # Each bar should have specific properties
        for trace in fig.data:
            self.assertIn(trace.name, ["GPU Type", "GPU Count", "Instance Type"])
            
            # Should have as many bars as configurations
            self.assertEqual(len(trace.x), 3)

if __name__ == "__main__":
    unittest.main()