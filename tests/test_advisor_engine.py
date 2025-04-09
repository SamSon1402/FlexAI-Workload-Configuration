import unittest
import sys
import os

# Add the parent directory to the path so we can import the src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.advisor_engine import (
    generate_recommendation, 
    apply_heuristics, 
    adjust_for_priority, 
    adjust_for_constraints,
    calculate_estimates
)

class TestAdvisorEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test resources and inputs"""
        # Sample resources for testing
        self.test_resources = {
            "gpu_types": {
                "NVIDIA T4": {
                    "description": "Entry-level GPU",
                    "vram": "16 GB",
                    "relative_performance": 1.0,
                    "hourly_cost": 0.76,
                    "suitable_for": ["Inference", "Small Training"],
                    "availability": "High"
                },
                "NVIDIA A100": {
                    "description": "High-performance GPU",
                    "vram": "40 GB",
                    "relative_performance": 5.0,
                    "hourly_cost": 2.89,
                    "suitable_for": ["Large Model Training", "Fine-tuning"],
                    "availability": "Limited"
                }
            },
            "instance_types": {
                "flex-economy": {
                    "description": "Preemptible instances",
                    "cpu_ram": "16 GB",
                    "cost_multiplier": 0.6,
                    "reliability": "Medium",
                    "suitable_for": ["Batch processing"]
                },
                "flex-standard": {
                    "description": "Standard instances",
                    "cpu_ram": "32 GB",
                    "cost_multiplier": 1.0,
                    "reliability": "High",
                    "suitable_for": ["Training", "Inference"]
                }
            }
        }
        
        # Sample input for testing
        self.test_input = {
            "task_type": "Training",
            "model_size": "Large",
            "dataset_size": "Medium (1GB-10GB)",
            "framework": "PyTorch",
            "priority": "Balanced",
            "budget_limit": None,
            "deadline": None
        }
    
    def test_apply_heuristics(self):
        """Test that heuristics are correctly applied based on workload"""
        recommendation = {
            "gpu_type": "",
            "gpu_count": 0,
            "instance_type": "",
            "region": "us-east"
        }
        
        # Test for Training + Large model
        result = apply_heuristics(
            recommendation, 
            "Training", 
            "Large", 
            "Medium (1GB-10GB)"
        )
        
        self.assertEqual(result["gpu_type"], "NVIDIA A100")
        self.assertEqual(result["gpu_count"], 4)
        self.assertEqual(result["instance_type"], "flex-performance")
        
        # Test for Batch Inference + Small model
        result = apply_heuristics(
            recommendation, 
            "Batch Inference", 
            "Small", 
            "Small (<1GB)"
        )
        
        self.assertEqual(result["gpu_type"], "NVIDIA T4")
        self.assertEqual(result["gpu_count"], 2)
        self.assertEqual(result["instance_type"], "flex-economy")
    
    def test_adjust_for_priority(self):
        """Test that recommendations are adjusted based on priority"""
        # Start with a basic recommendation
        recommendation = {
            "gpu_type": "NVIDIA A100",
            "gpu_count": 2,
            "instance_type": "flex-standard",
            "region": "us-east"
        }
        
        # Test cost optimization
        cost_result = adjust_for_priority(
            recommendation.copy(),
            "Training",
            "Large",
            "Minimize Cost",
            self.test_resources
        )
        
        # Should downgrade to economy for cost savings
        self.assertEqual(cost_result["instance_type"], "flex-economy")
        
        # Test performance optimization
        perf_result = adjust_for_priority(
            recommendation.copy(),
            "Training",
            "Large",
            "Minimize Time",
            self.test_resources
        )
        
        # Should upgrade to performance instance and increase GPU count
        self.assertEqual(perf_result["instance_type"], "flex-performance")
        self.assertGreater(perf_result["gpu_count"], recommendation["gpu_count"])
    
    def test_adjust_for_constraints(self):
        """Test that recommendations are adjusted based on constraints"""
        # Start with an expensive recommendation
        recommendation = {
            "gpu_type": "NVIDIA A100",
            "gpu_count": 4,
            "instance_type": "flex-standard",
            "region": "us-east"
        }
        
        # Test budget constraint
        # Budget limit of $5/hour (should reduce GPU count)
        budget_result = adjust_for_constraints(
            recommendation.copy(),
            5.0,
            None,
            self.test_resources
        )
        
        # Calculate the cost of the original vs adjusted recommendation
        original_cost = self.test_resources["gpu_types"]["NVIDIA A100"]["hourly_cost"] * 4 * self.test_resources["instance_types"]["flex-standard"]["cost_multiplier"]
        adjusted_cost = self.test_resources["gpu_types"][budget_result["gpu_type"]]["hourly_cost"] * budget_result["gpu_count"] * self.test_resources["instance_types"][budget_result["instance_type"]]["cost_multiplier"]
        
        # Adjusted cost should be within budget
        self.assertLessEqual(adjusted_cost, 5.0)
        self.assertLess(adjusted_cost, original_cost)
    
    def test_generate_recommendation(self):
        """Test the full recommendation generation process"""
        result = generate_recommendation(self.test_input)
        
        # Check that the result has all expected fields
        expected_fields = [
            "gpu_type", "gpu_count", "instance_type", "region",
            "estimated_cost", "estimated_time", "justification", "alternatives"
        ]
        for field in expected_fields:
            self.assertIn(field, result)
        
        # Check that justification is a non-empty list
        self.assertIsInstance(result["justification"], list)
        self.assertGreater(len(result["justification"]), 0)
        
        # Check that alternatives is a list
        self.assertIsInstance(result["alternatives"], list)

if __name__ == "__main__":
    unittest.main()