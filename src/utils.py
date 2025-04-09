def hex_to_rgba(hex_color, alpha):
    """
    Convert hex color to rgba format with given alpha
    
    Args:
        hex_color: Hex color code (e.g., "#6200ea")
        alpha: Alpha value between 0 and 1
        
    Returns:
        str: RGBA color string
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    return hex_color  # Return as is if not a valid hex

def calculate_total_cost(hourly_cost, time_estimate, return_numeric=False):
    """
    Calculate approximate total cost based on hourly rate and time estimate
    
    Args:
        hourly_cost: Cost per hour
        time_estimate: Time estimate string (e.g., "30 minutes" or "2.5 hours")
        return_numeric: Whether to return a numeric value or formatted string
        
    Returns:
        float or str: Total cost
    """
    if "Real-time" in time_estimate or "ms" in time_estimate:
        if return_numeric:
            return hourly_cost * 24  # Assume 24 hours for demonstration
        return f"{hourly_cost * 24} (daily)"
    
    # Extract time value
    if "minutes" in time_estimate:
        time_value = float(time_estimate.split(" ")[0])
        hours = time_value / 60
    else:
        time_value = float(time_estimate.split(" ")[0])
        hours = time_value
    
    total_cost = hourly_cost * hours
    
    if return_numeric:
        return round(total_cost, 2)
    
    return f"{round(total_cost, 2)}"

def get_alt_time_estimate(recommendation, alternative):
    """
    Generate time estimate for alternative based on primary recommendation
    
    Args:
        recommendation: Primary recommendation dictionary
        alternative: Alternative configuration dictionary
        
    Returns:
        str: Time estimate string
    """
    if "Real-time" in recommendation["estimated_time"]:
        return "Low latency (ms)"
    
    # If alternative is budget option, estimate 30% slower
    if alternative["name"] == "Budget Option":
        if "minutes" in recommendation["estimated_time"]:
            time_value = float(recommendation["estimated_time"].split(" ")[0])
            new_time = time_value * 1.3
            return f"{int(new_time)} minutes" if new_time < 60 else f"{new_time/60:.1f} hours"
        else:
            time_value = float(recommendation["estimated_time"].split(" ")[0])
            new_time = time_value * 1.3
            return f"{new_time:.1f} hours"
    
    # If alternative is performance option, estimate 30% faster
    if alternative["name"] == "Performance Option":
        if "minutes" in recommendation["estimated_time"]:
            time_value = float(recommendation["estimated_time"].split(" ")[0])
            new_time = time_value * 0.7
            return f"{int(new_time)} minutes" if new_time < 60 else f"{new_time/60:.1f} hours"
        else:
            time_value = float(recommendation["estimated_time"].split(" ")[0])
            new_time = time_value * 0.7
            return f"{new_time:.1f} hours"
    
    return recommendation["estimated_time"]

def estimate_memory_requirement(model_size, task_type):
    """
    Estimate memory requirement based on model size and task
    
    Args:
        model_size: Size of the model (Small, Medium, Large, XL)
        task_type: Type of task
        
    Returns:
        int: Estimated memory in GB
    """
    # Base memory requirements by model size
    memory_by_size = {
        "Small": 8,
        "Medium": 16,
        "Large": 40,
        "XL": 80
    }
    
    # Task type multipliers
    task_multipliers = {
        "Training": 1.5,
        "Fine-tuning": 1.2,
        "Batch Inference": 0.8,
        "Real-time Inference": 0.6
    }
    
    base_memory = memory_by_size.get(model_size, 16)
    multiplier = task_multipliers.get(task_type, 1.0)
    
    return int(base_memory * multiplier)

def format_price(price):
    """
    Format price with proper currency symbol and decimals
    
    Args:
        price: Price value
        
    Returns:
        str: Formatted price string
    """
    return f"${price:.2f}"