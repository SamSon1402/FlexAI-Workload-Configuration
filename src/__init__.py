# Import main modules to make them available through the package
from .advisor_engine import generate_recommendation, apply_heuristics, adjust_for_constraints
from .visualizations import create_cost_time_comparison, create_resource_comparison_chart
from .simulator import simulate_advisor_processing
from .utils import calculate_total_cost, hex_to_rgba