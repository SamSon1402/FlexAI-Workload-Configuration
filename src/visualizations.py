import plotly.express as px
import plotly.graph_objects as go
from .utils import hex_to_rgba

def create_cost_time_comparison(recommendation, alternatives):
    """
    Create a cost vs. time comparison chart
    
    Args:
        recommendation: Primary recommendation dictionary
        alternatives: List of alternative configurations
        
    Returns:
        Plotly figure object or None if no valid data
    """
    # Create comparison data
    data = []
    
    # Add primary recommendation
    if "Real-time" not in recommendation["estimated_time"]:
        # Convert estimated time to hours
        time_str = recommendation["estimated_time"]
        if "minutes" in time_str:
            time_hours = float(time_str.split(" ")[0]) / 60
        else:
            time_hours = float(time_str.split(" ")[0])
            
        data.append({
            "Configuration": "Recommended",
            "Hourly Cost ($)": recommendation["estimated_cost"],
            "Estimated Time (hours)": time_hours,
            "Total Cost ($)": round(recommendation["estimated_cost"] * time_hours, 2),
            "Description": "Primary Recommendation"
        })
    
    # Add alternatives (if they have time estimates)
    for alt in alternatives:
        if "name" in alt and "Real-time" not in alt.get("estimated_time", ""):
            # Estimate time - assume 30% slower for budget, 30% faster for performance
            if alt["name"] == "Budget Option":
                if "minutes" in recommendation["estimated_time"]:
                    time_str = recommendation["estimated_time"]
                    base_minutes = float(time_str.split(" ")[0])
                    time_hours = (base_minutes * 1.3) / 60
                else:
                    time_str = recommendation["estimated_time"]
                    base_hours = float(time_str.split(" ")[0])
                    time_hours = base_hours * 1.3
            elif alt["name"] == "Performance Option":
                if "minutes" in recommendation["estimated_time"]:
                    time_str = recommendation["estimated_time"]
                    base_minutes = float(time_str.split(" ")[0])
                    time_hours = (base_minutes * 0.7) / 60
                else:
                    time_str = recommendation["estimated_time"]
                    base_hours = float(time_str.split(" ")[0])
                    time_hours = base_hours * 0.7
            
            data.append({
                "Configuration": alt["name"],
                "Hourly Cost ($)": alt["estimated_cost"],
                "Estimated Time (hours)": time_hours,
                "Total Cost ($)": round(alt["estimated_cost"] * time_hours, 2),
                "Description": alt["description"]
            })
    
    if not data:  # If no valid data (e.g., real-time inference only)
        return None
    
    # Create dataframe
    import pandas as pd
    df = pd.DataFrame(data)
    
    # Create figure
    fig = px.scatter(
        df,
        x="Estimated Time (hours)",
        y="Hourly Cost ($)",
        size="Total Cost ($)",
        color="Configuration",
        size_max=40,
        text="Configuration",
        title="Cost vs. Time Comparison",
        color_discrete_sequence=["#6200ea", "#ff9800", "#00bcd4"]
    )
    
    # Update layout
    fig.update_layout(
        font_family="Roboto Mono, monospace",
        font_color="#0a0a20",
        title_font_family="VT323, monospace",
        title_font_color="#6200ea",
        title_font_size=24,
        plot_bgcolor="#f5f0ff",
        paper_bgcolor="#f5f0ff",
        xaxis=dict(
            title_font_family="Roboto Mono, monospace",
            title_font_color="#0a0a20",
            tickfont_family="Roboto Mono, monospace",
            tickfont_color="#0a0a20",
            gridcolor="#e0aaff",
            gridwidth=0.5,
        ),
        yaxis=dict(
            title_font_family="Roboto Mono, monospace",
            title_font_color="#0a0a20",
            tickfont_family="Roboto Mono, monospace",
            tickfont_color="#0a0a20",
            gridcolor="#e0aaff",
            gridwidth=0.5,
        ),
    )
    
    # Add text labels
    fig.update_traces(
        textposition="top center",
        textfont=dict(
            family="VT323, monospace",
            size=14,
            color="#6200ea"
        )
    )
    
    # Add a note about the bubble size representing total cost
    fig.add_annotation(
        text="Bubble size represents total cost ($)",
        x=0.5,
        y=-0.15,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(
            family="Roboto Mono, monospace",
            size=12,
            color="#0a0a20"
        )
    )
    
    return fig

def create_resource_comparison_chart(recommendation, alternatives):
    """
    Create a bar chart comparing resources across configurations
    
    Args:
        recommendation: Primary recommendation dictionary
        alternatives: List of alternative configurations
        
    Returns:
        Plotly figure object
    """
    # Create comparison data
    data = []
    
    # Add primary recommendation
    data.append({
        "Configuration": "Recommended",
        "GPU Type": recommendation["gpu_type"],
        "GPU Count": recommendation["gpu_count"],
        "Instance Type": recommendation["instance_type"],
        "Hourly Cost ($)": recommendation["estimated_cost"],
        "Color": "#6200ea"
    })
    
    # Add alternatives
    for alt in alternatives:
        if "name" in alt:
            data.append({
                "Configuration": alt["name"],
                "GPU Type": alt["gpu_type"],
                "GPU Count": alt["gpu_count"],
                "Instance Type": alt["instance_type"],
                "Hourly Cost ($)": alt["estimated_cost"],
                "Color": "#ff9800" if alt["name"] == "Budget Option" else "#00bcd4"
            })
    
    # Create dataframe
    import pandas as pd
    df = pd.DataFrame(data)
    
    # Create grouped bar chart for resources
    fig = go.Figure()
    
    # Add GPU Type bars
    fig.add_trace(go.Bar(
        x=df["Configuration"],
        y=[1] * len(df),  # Same height for all
        text=df["GPU Type"],
        name="GPU Type",
        marker_color=df["Color"],
        textposition="inside",
        insidetextfont=dict(
            family="Roboto Mono, monospace",
            size=12,
            color="white"
        ),
        hovertemplate="GPU Type: %{text}<extra></extra>"
    ))
    
    # Add GPU Count bars
    fig.add_trace(go.Bar(
        x=df["Configuration"],
        y=[0.5] * len(df),  # Half height
        text=df["GPU Count"].apply(lambda x: f"{x} GPU(s)"),
        name="GPU Count",
        marker_color=[hex_to_rgba(color, 0.7) for color in df["Color"]],
        textposition="inside",
        insidetextfont=dict(
            family="Roboto Mono, monospace",
            size=12,
            color="white"
        ),
        hovertemplate="GPU Count: %{text}<extra></extra>"
    ))
    
    # Add Instance Type bars
    fig.add_trace(go.Bar(
        x=df["Configuration"],
        y=[0.5] * len(df),  # Half height
        text=df["Instance Type"],
        name="Instance Type",
        marker_color=[hex_to_rgba(color, 0.4) for color in df["Color"]],
        textposition="inside",
        insidetextfont=dict(
            family="Roboto Mono, monospace",
            size=12,
            color="white"
        ),
        hovertemplate="Instance Type: %{text}<extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title="Resource Comparison",
        title_font=dict(
            family="VT323, monospace",
            size=24,
            color="#6200ea"
        ),
        font=dict(
            family="Roboto Mono, monospace",
            color="#0a0a20"
        ),
        barmode="stack",
        showlegend=False,
        plot_bgcolor="#f5f0ff",
        paper_bgcolor="#f5f0ff",
        xaxis=dict(
            title="Configuration Options",
            title_font_family="Roboto Mono, monospace",
            title_font_color="#0a0a20",
            tickfont_family="Roboto Mono, monospace",
            tickfont_color="#0a0a20",
            gridcolor="#e0aaff",
            gridwidth=0.5,
        ),
        yaxis=dict(
            visible=False
        ),
    )
    
    # Add cost annotations
    for i, row in df.iterrows():
        fig.add_annotation(
            text=f"${row['Hourly Cost ($)']} / hour",
            x=row["Configuration"],
            y=2.1,
            showarrow=False,
            font=dict(
                family="VT323, monospace",
                size=16,
                color="#6200ea"
            )
        )
    
    return fig

def create_performance_radar_chart(recommendation, alternatives, resources):
    """
    Create a radar chart comparing performance dimensions
    
    Args:
        recommendation: Primary recommendation dictionary
        alternatives: List of alternative configurations
        resources: Resource configurations
        
    Returns:
        Plotly figure object
    """
    # Performance dimensions to compare
    dimensions = ["Compute Power", "Cost Efficiency", "Reliability", "Scalability", "Memory"]
    
    # Create comparison data
    data = []
    
    # Add primary recommendation
    primary_scores = calculate_performance_scores(recommendation, resources)
    primary_scores_list = [primary_scores[dim] for dim in dimensions]
    # Add the first dimension again at the end to close the polygon
    primary_scores_list.append(primary_scores_list[0])
    
    data.append({
        "Configuration": "Recommended",
        "Scores": primary_scores_list,
        "Color": "#6200ea"
    })
    
    # Add alternatives
    for alt in alternatives:
        if "name" in alt:
            alt_scores = calculate_performance_scores(alt, resources)
            alt_scores_list = [alt_scores[dim] for dim in dimensions]
            # Add the first dimension again at the end to close the polygon
            alt_scores_list.append(alt_scores_list[0])
            
            data.append({
                "Configuration": alt["name"],
                "Scores": alt_scores_list,
                "Color": "#ff9800" if alt["name"] == "Budget Option" else "#00bcd4"
            })
    
    # Create the radar chart
    fig = go.Figure()
    
    # Add a trace for each configuration
    for item in data:
        fig.add_trace(go.Scatterpolar(
            r=item["Scores"],
            theta=dimensions + [dimensions[0]],  # Repeat first dimension to close the polygon
            name=item["Configuration"],
            line=dict(color=item["Color"], width=3),
            fill='toself',
            fillcolor=hex_to_rgba(item["Color"], 0.2)
        ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(
                    family="Roboto Mono, monospace",
                    size=10,
                    color="#0a0a20"
                ),
                gridcolor="#e0aaff",
                gridwidth=0.5
            ),
            angularaxis=dict(
                tickfont=dict(
                    family="Roboto Mono, monospace",
                    size=12,
                    color="#0a0a20"
                ),
                gridcolor="#e0aaff",
                gridwidth=0.5
            ),
            bgcolor="#f5f0ff"
        ),
        title=dict(
            text="Performance Comparison",
            font=dict(
                family="VT323, monospace",
                size=24,
                color="#6200ea"
            )
        ),
        font=dict(
            family="Roboto Mono, monospace",
            color="#0a0a20"
        ),
        paper_bgcolor="#f5f0ff",
        showlegend=True,
        legend=dict(
            font=dict(
                family="Roboto Mono, monospace",
                size=12,
                color="#0a0a20"
            )
        )
    )
    
    return fig

def calculate_performance_scores(config, resources):
    """
    Calculate performance scores for radar chart
    
    Args:
        config: Configuration dictionary
        resources: Resource configurations
        
    Returns:
        Dictionary of scores for different dimensions
    """
    scores = {}
    
    # Get GPU performance factor
    gpu_perf = resources["gpu_types"][config["gpu_type"]]["relative_performance"]
    
    # Get instance reliability factor
    instance_reliability = {
        "flex-economy": 0.6,
        "flex-standard": 0.8,
        "flex-performance": 1.0
    }
    
    # Calculate scores
    scores["Compute Power"] = min(10, gpu_perf * config["gpu_count"] * 0.8)
    
    # Cost efficiency is inverse of cost (higher = more efficient)
    base_cost = 5.76 * 8  # Max cost (H100 x 8)
    config_cost = config["estimated_cost"]
    scores["Cost Efficiency"] = min(10, 10 * (1 - config_cost / base_cost))
    
    # Reliability based on instance type
    scores["Reliability"] = min(10, instance_reliability[config["instance_type"]] * 10)
    
    # Scalability based on GPU count and type
    scores["Scalability"] = min(10, config["gpu_count"] * 1.5)
    
    # Memory based on GPU type
    gpu_memory = {
        "NVIDIA T4": 0.5,
        "NVIDIA A10G": 0.7,
        "NVIDIA A100": 0.9,
        "NVIDIA H100": 1.0
    }
    scores["Memory"] = min(10, gpu_memory[config["gpu_type"]] * 10)
    
    return scores