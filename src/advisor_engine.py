import json
import os
import datetime
from .utils import calculate_total_cost

def load_resource_configs(file_path="data/resource_configs.json"):
    """
    Load resource configurations from JSON file
    
    Args:
        file_path (str): Path to the resource configs JSON file
        
    Returns:
        dict: Resource configurations
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default configs if file not found
        return {
            "gpu_types": {
                "NVIDIA T4": {
                    "description": "Entry-level GPU good for small models and inference",
                    "vram": "16 GB",
                    "relative_performance": 1.0,
                    "hourly_cost": 0.76,
                    "suitable_for": ["Inference", "Small Training"],
                    "availability": "High"
                },
                "NVIDIA A10G": {
                    "description": "Mid-range GPU for most training tasks",
                    "vram": "24 GB",
                    "relative_performance": 2.5,
                    "hourly_cost": 1.40,
                    "suitable_for": ["Training", "Fine-tuning", "Inference"],
                    "availability": "Medium"
                },
                "NVIDIA A100": {
                    "description": "High-performance GPU for large models and training",
                    "vram": "40/80 GB",
                    "relative_performance": 5.0,
                    "hourly_cost": 2.89,
                    "suitable_for": ["Large Model Training", "Fine-tuning"],
                    "availability": "Limited"
                },
                "NVIDIA H100": {
                    "description": "Cutting-edge GPU for the most demanding workloads",
                    "vram": "80 GB",
                    "relative_performance": 8.0,
                    "hourly_cost": 5.76,
                    "suitable_for": ["XL Model Training", "Research"],
                    "availability": "Very Limited"
                }
            },
            "instance_types": {
                "flex-economy": {
                    "description": "Preemptible instances with lower cost but potential interruptions",
                    "cpu_ram": "16-32 GB",
                    "cost_multiplier": 0.6,
                    "reliability": "Medium",
                    "suitable_for": ["Batch processing", "Non-critical workloads"]
                },
                "flex-standard": {
                    "description": "Standard reliable instances for most workloads",
                    "cpu_ram": "32-64 GB",
                    "cost_multiplier": 1.0,
                    "reliability": "High",
                    "suitable_for": ["Training", "Fine-tuning", "Inference"]
                },
                "flex-performance": {
                    "description": "High-performance instances with optimized networking",
                    "cpu_ram": "64-128 GB",
                    "cost_multiplier": 1.4,
                    "reliability": "Very High",
                    "suitable_for": ["Distributed training", "Critical workloads"]
                }
            },
            "regions": [
                "us-east", "us-west", "europe-west", "asia-east"
            ],
            "frameworks": [
                "PyTorch", "TensorFlow", "JAX", "MXNet"
            ]
        }

def load_heuristics(file_path="data/heuristics.json"):
    """
    Load heuristic rules from JSON file
    
    Args:
        file_path (str): Path to the heuristics JSON file
        
    Returns:
        dict: Heuristic rules
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return empty dict if file not found
        return {}

def generate_recommendation(input_data):
    """
    Generate resource recommendations based on user input.
    
    Args:
        input_data: Dictionary containing user inputs
        
    Returns:
        Dictionary with recommendations
    """
    # Load resource configurations
    resources = load_resource_configs()
    
    # Extract input variables
    task_type = input_data["task_type"]
    model_size = input_data["model_size"]
    dataset_size = input_data["dataset_size"]
    framework = input_data["framework"]
    priority = input_data["priority"]
    budget_limit = input_data["budget_limit"]
    deadline = input_data["deadline"]
    
    # Default recommendations
    recommendation = {
        "gpu_type": "NVIDIA A10G",
        "gpu_count": 2,
        "instance_type": "flex-standard",
        "region": "us-east",
        "estimated_cost": 0,
        "estimated_time": 0,
        "justification": "",
        "alternatives": []
    }
    
    # Apply base heuristics
    recommendation = apply_heuristics(recommendation, task_type, model_size, dataset_size)
    
    # Adjust based on priority
    recommendation = adjust_for_priority(recommendation, task_type, model_size, priority, resources)
    
    # Apply constraints
    recommendation = adjust_for_constraints(recommendation, budget_limit, deadline, resources)
    
    # Calculate cost and time estimates
    recommendation = calculate_estimates(recommendation, task_type, model_size, dataset_size, resources)
    
    # Generate justification
    recommendation["justification"] = generate_justification(recommendation, input_data, resources)
    
    # Generate alternatives
    recommendation["alternatives"] = generate_alternatives(recommendation, input_data, resources)
    
    return recommendation

def apply_heuristics(recommendation, task_type, model_size, dataset_size):
    """
    Apply basic heuristic rules based on workload characteristics
    
    Args:
        recommendation: Initial recommendation dict
        task_type: Type of task (Training, Fine-tuning, etc.)
        model_size: Size of model (Small, Medium, Large, XL)
        dataset_size: Size of dataset
        
    Returns:
        Updated recommendation dict
    """
    # Apply heuristics based on task type
    if task_type == "Training":
        if model_size == "XL":
            recommendation["gpu_type"] = "NVIDIA H100"
            recommendation["gpu_count"] = 4
            recommendation["instance_type"] = "flex-performance"
        elif model_size == "Large":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 4
            recommendation["instance_type"] = "flex-performance"
        elif model_size == "Medium":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-standard"
        else:  # Small
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-standard"
    
    elif task_type == "Fine-tuning":
        if model_size == "XL":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-standard"
        elif model_size == "Large":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
        elif model_size == "Medium":
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-standard"
        else:  # Small
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
    
    elif task_type == "Batch Inference":
        if model_size == "XL":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
        elif model_size == "Large":
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-standard"
        elif model_size == "Medium":
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
        else:  # Small
            recommendation["gpu_type"] = "NVIDIA T4"
            recommendation["gpu_count"] = 2
            recommendation["instance_type"] = "flex-economy"
    
    elif task_type == "Real-time Inference":
        if model_size == "XL":
            recommendation["gpu_type"] = "NVIDIA A100"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-performance"
        elif model_size == "Large":
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-performance"
        elif model_size == "Medium":
            recommendation["gpu_type"] = "NVIDIA A10G"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
        else:  # Small
            recommendation["gpu_type"] = "NVIDIA T4"
            recommendation["gpu_count"] = 1
            recommendation["instance_type"] = "flex-standard"
    
    # Adjust based on dataset size
    if dataset_size == "Very Large (>1TB)":
        recommendation["gpu_count"] = min(8, recommendation["gpu_count"] * 2)
    elif dataset_size == "Large (100GB-1TB)":
        recommendation["gpu_count"] = min(4, recommendation["gpu_count"] + 1)
    
    return recommendation

def adjust_for_priority(recommendation, task_type, model_size, priority, resources):
    """
    Adjust recommendation based on user priority
    
    Args:
        recommendation: Current recommendation dict
        task_type: Type of task
        model_size: Size of model
        priority: User priority (Minimize Cost, Minimize Time, Balanced)
        resources: Resource configuration data
        
    Returns:
        Updated recommendation dict
    """
    if priority == "Minimize Cost":
        # Downgrade if possible
        if recommendation["gpu_type"] == "NVIDIA H100" and model_size != "XL":
            recommendation["gpu_type"] = "NVIDIA A100"
        elif recommendation["gpu_type"] == "NVIDIA A100" and model_size in ["Small", "Medium"]:
            recommendation["gpu_type"] = "NVIDIA A10G"
            
        # Reduce instance type if not real-time
        if task_type != "Real-time Inference" and recommendation["instance_type"] == "flex-performance":
            recommendation["instance_type"] = "flex-standard"
            
        # Use preemptible instances for non-critical workloads
        if task_type in ["Training", "Batch Inference"]:
            recommendation["instance_type"] = "flex-economy"
            
    elif priority == "Minimize Time":
        # Upgrade if possible
        if recommendation["gpu_type"] == "NVIDIA A10G" and model_size in ["Medium", "Large"]:
            recommendation["gpu_type"] = "NVIDIA A100"
        elif recommendation["gpu_type"] == "NVIDIA A100" and model_size == "XL":
            recommendation["gpu_type"] = "NVIDIA H100"
            
        # Increase instance type for better performance
        if recommendation["instance_type"] == "flex-standard" and task_type in ["Training", "Fine-tuning", "Real-time Inference"]:
            recommendation["instance_type"] = "flex-performance"
            
        # Increase GPU count if large workload
        if task_type in ["Training", "Fine-tuning"] and model_size in ["Large", "XL"]:
            recommendation["gpu_count"] = min(8, recommendation["gpu_count"] + 2)
    
    return recommendation

def adjust_for_constraints(recommendation, budget_limit, deadline, resources):
    """
    Adjust recommendation based on budget and deadline constraints
    
    Args:
        recommendation: Current recommendation dict
        budget_limit: Maximum hourly budget (if any)
        deadline: Deadline constraint (if any)
        resources: Resource configuration data
        
    Returns:
        Updated recommendation dict
    """
    # Apply budget limit if specified
    if budget_limit:
        # Estimate cost
        gpu_hourly_cost = resources["gpu_types"][recommendation["gpu_type"]]["hourly_cost"]
        instance_multiplier = resources["instance_types"][recommendation["instance_type"]]["cost_multiplier"]
        estimated_hourly_cost = gpu_hourly_cost * recommendation["gpu_count"] * instance_multiplier
        
        # If over budget, adjust
        if estimated_hourly_cost > budget_limit:
            # Try reducing GPU count
            if recommendation["gpu_count"] > 1:
                recommendation["gpu_count"] -= 1
            # If still over budget, downgrade GPU type
            gpu_hourly_cost = resources["gpu_types"][recommendation["gpu_type"]]["hourly_cost"]
            estimated_hourly_cost = gpu_hourly_cost * recommendation["gpu_count"] * instance_multiplier
            
            if estimated_hourly_cost > budget_limit:
                if recommendation["gpu_type"] == "NVIDIA H100":
                    recommendation["gpu_type"] = "NVIDIA A100"
                elif recommendation["gpu_type"] == "NVIDIA A100":
                    recommendation["gpu_type"] = "NVIDIA A10G"
                elif recommendation["gpu_type"] == "NVIDIA A10G":
                    recommendation["gpu_type"] = "NVIDIA T4"
            
            # If still over budget, downgrade instance type
            gpu_hourly_cost = resources["gpu_types"][recommendation["gpu_type"]]["hourly_cost"]
            estimated_hourly_cost = gpu_hourly_cost * recommendation["gpu_count"] * instance_multiplier
            
            if estimated_hourly_cost > budget_limit and recommendation["instance_type"] != "flex-economy":
                if recommendation["instance_type"] == "flex-performance":
                    recommendation["instance_type"] = "flex-standard"
                elif recommendation["instance_type"] == "flex-standard":
                    recommendation["instance_type"] = "flex-economy"
    
    # Future enhancement: Add deadline-based adjustments
    
    return recommendation

def calculate_estimates(recommendation, task_type, model_size, dataset_size, resources):
    """
    Calculate cost and time estimates for the recommendation
    
    Args:
        recommendation: Current recommendation dict
        task_type: Type of task
        model_size: Size of model
        dataset_size: Size of dataset
        resources: Resource configuration data
        
    Returns:
        Updated recommendation dict with estimates
    """
    # Calculate final estimated cost
    gpu_hourly_cost = resources["gpu_types"][recommendation["gpu_type"]]["hourly_cost"]
    instance_multiplier = resources["instance_types"][recommendation["instance_type"]]["cost_multiplier"]
    recommendation["estimated_cost"] = round(gpu_hourly_cost * recommendation["gpu_count"] * instance_multiplier, 2)
    
    # Estimate time based on performance
    base_hours = {
        "Training": {"Small": 2, "Medium": 6, "Large": 24, "XL": 72},
        "Fine-tuning": {"Small": 1, "Medium": 3, "Large": 10, "XL": 24},
        "Batch Inference": {"Small": 0.5, "Medium": 1, "Large": 3, "XL": 8},
        "Real-time Inference": {"Small": 0, "Medium": 0, "Large": 0, "XL": 0}  # Real-time is measured differently
    }
    
    if task_type == "Real-time Inference":
        recommendation["estimated_time"] = "Low latency (ms)"
    else:
        # Base time for the task and model size
        base_time = base_hours[task_type][model_size]
        
        # Adjust for dataset size
        dataset_multipliers = {
            "Small (<1GB)": 0.5,
            "Medium (1GB-10GB)": 1.0,
            "Large (10GB-100GB)": 2.0,
            "Very Large (>100GB)": 4.0
        }
        
        # Adjust for GPU performance and count
        performance_factor = resources["gpu_types"][recommendation["gpu_type"]]["relative_performance"]
        parallelization_efficiency = 0.7  # Diminishing returns with more GPUs
        
        gpu_perf_factor = performance_factor * (1 + (recommendation["gpu_count"] - 1) * parallelization_efficiency) / recommendation["gpu_count"]
        
        # Final time estimate
        estimated_hours = base_time * dataset_multipliers[dataset_size] / gpu_perf_factor
        
        if estimated_hours < 1:
            recommendation["estimated_time"] = f"{int(estimated_hours * 60)} minutes"
        else:
            recommendation["estimated_time"] = f"{estimated_hours:.1f} hours"
    
    return recommendation

def generate_justification(recommendation, input_data, resources):
    """
    Generate explanation for the recommendation
    
    Args:
        recommendation: Generated recommendation
        input_data: User input data
        resources: Resource configuration data
        
    Returns:
        List of justification points
    """
    task_type = input_data["task_type"]
    model_size = input_data["model_size"]
    priority = input_data["priority"]
    
    gpu_type = recommendation["gpu_type"]
    gpu_count = recommendation["gpu_count"]
    instance_type = recommendation["instance_type"]
    
    justification = []
    
    # GPU type justification
    gpu_desc = resources["gpu_types"][gpu_type]["description"]
    justification.append(f"**GPU Selection ({gpu_type}):** {gpu_desc}")
    
    # GPU count justification
    if gpu_count > 1:
        if task_type in ["Training", "Fine-tuning"]:
            justification.append(f"**Multiple GPUs ({gpu_count}):** Recommended for {model_size.lower()} model {task_type.lower()} to distribute the workload and reduce total processing time.")
        else:
            justification.append(f"**Multiple GPUs ({gpu_count}):** Recommended for high-throughput {task_type.lower()} of {model_size.lower()} models.")
    else:
        justification.append(f"**Single GPU:** Sufficient for {model_size.lower()} model {task_type.lower()} with your specified requirements.")
    
    # Instance type justification
    instance_desc = resources["instance_types"][instance_type]["description"]
    justification.append(f"**Instance Type ({instance_type}):** {instance_desc}")
    
    # Priority-based justification
    if priority == "Minimize Cost":
        justification.append(f"**Cost Optimization:** This configuration balances performance needs while keeping costs lower, as per your priority.")
    elif priority == "Minimize Time":
        justification.append(f"**Performance Optimization:** This configuration prioritizes speed and processing power, as per your priority.")
    else:  # Balanced
        justification.append(f"**Balanced Approach:** This configuration offers a good balance between cost efficiency and performance.")
    
    # Budget considerations
    if input_data["budget_limit"]:
        justification.append(f"**Budget Consideration:** Configuration designed to stay within your specified budget limit of ${input_data['budget_limit']}/hour.")
    
    # Deadline considerations
    if input_data["deadline"]:
        justification.append(f"**Deadline Consideration:** Configuration designed to help meet your specified deadline.")
    
    return justification

def generate_alternatives(recommendation, input_data, resources):
    """
    Generate alternative configurations
    
    Args:
        recommendation: Primary recommendation
        input_data: User input data
        resources: Resource configuration data
        
    Returns:
        List of alternative configurations
    """
    alternatives = []
    
    # Alternative 1: More cost-effective option
    if recommendation["gpu_type"] != "NVIDIA T4" or recommendation["instance_type"] != "flex-economy":
        cost_effective = recommendation.copy()
        
        # Downgrade GPU if possible
        if cost_effective["gpu_type"] == "NVIDIA H100":
            cost_effective["gpu_type"] = "NVIDIA A100"
        elif cost_effective["gpu_type"] == "NVIDIA A100":
            cost_effective["gpu_type"] = "NVIDIA A10G"
        elif cost_effective["gpu_type"] == "NVIDIA A10G":
            cost_effective["gpu_type"] = "NVIDIA T4"
        
        # Downgrade instance type if not already economy
        if cost_effective["instance_type"] != "flex-economy":
            if cost_effective["instance_type"] == "flex-performance":
                cost_effective["instance_type"] = "flex-standard"
            elif cost_effective["instance_type"] == "flex-standard":
                cost_effective["instance_type"] = "flex-economy"
        
        # Calculate new cost
        gpu_hourly_cost = resources["gpu_types"][cost_effective["gpu_type"]]["hourly_cost"]
        instance_multiplier = resources["instance_types"][cost_effective["instance_type"]]["cost_multiplier"]
        cost_effective["estimated_cost"] = round(gpu_hourly_cost * cost_effective["gpu_count"] * instance_multiplier, 2)
        
        # Add cost savings percentage
        original_cost = recommendation["estimated_cost"]
        new_cost = cost_effective["estimated_cost"]
        savings_pct = round((original_cost - new_cost) / original_cost * 100)
        
        cost_effective["name"] = "Budget Option"
        cost_effective["description"] = f"A more cost-effective configuration saving {savings_pct}% on hourly costs."
        
        alternatives.append(cost_effective)
    
    # Alternative 2: High-performance option
    if recommendation["gpu_type"] != "NVIDIA H100" or recommendation["instance_type"] != "flex-performance":
        high_perf = recommendation.copy()
        
        # Upgrade GPU if possible
        if high_perf["gpu_type"] == "NVIDIA T4":
            high_perf["gpu_type"] = "NVIDIA A10G"
        elif high_perf["gpu_type"] == "NVIDIA A10G":
            high_perf["gpu_type"] = "NVIDIA A100"
        elif high_perf["gpu_type"] == "NVIDIA A100":
            high_perf["gpu_type"] = "NVIDIA H100"
        
        # Upgrade instance type if not already performance
        if high_perf["instance_type"] != "flex-performance":
            if high_perf["instance_type"] == "flex-economy":
                high_perf["instance_type"] = "flex-standard"
            elif high_perf["instance_type"] == "flex-standard":
                high_perf["instance_type"] = "flex-performance"
        
        # Calculate new cost
        gpu_hourly_cost = resources["gpu_types"][high_perf["gpu_type"]]["hourly_cost"]
        instance_multiplier = resources["instance_types"][high_perf["instance_type"]]["cost_multiplier"]
        high_perf["estimated_cost"] = round(gpu_hourly_cost * high_perf["gpu_count"] * instance_multiplier, 2)
        
        high_perf["name"] = "Performance Option"
        high_perf["description"] = "A higher-performance configuration for faster results."
        
        alternatives.append(high_perf)
    
    return alternatives