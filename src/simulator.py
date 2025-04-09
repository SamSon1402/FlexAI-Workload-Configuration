import time
import streamlit as st

def simulate_advisor_processing():
    """
    Simulate the advisor processing with an animated progress bar
    
    Returns:
        bool: Success status
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    phases = [
        "Analyzing workload requirements...",
        "Evaluating resource options...",
        "Calculating performance estimates...",
        "Optimizing for your priorities...",
        "Generating recommendations..."
    ]
    
    for i, phase in enumerate(phases):
        status_text.text(phase)
        progress_value = (i + 1) / len(phases)
        progress_bar.progress(progress_value)
        time.sleep(0.4)  # Simulate processing time
    
    status_text.text("Analysis complete!")
    time.sleep(0.3)
    return True

def create_animated_recommendation(recommendation):
    """
    Create a visually animated recommendation display
    
    Args:
        recommendation: The recommendation dictionary
        
    Returns:
        str: HTML for the animated recommendation
    """
    html = f"""
    <div class="recommendation-box pulse">
        <div class="recommendation-title">Recommended Configuration</div>
        <hr/>
        <div class="recommendation-subtitle">Resources</div>
        <div class="recommendation-detail">
            <strong>GPU Type:</strong> {recommendation["gpu_type"]}<br/>
            <strong>GPU Count:</strong> {recommendation["gpu_count"]}<br/>
            <strong>Instance Type:</strong> {recommendation["instance_type"]}<br/>
            <strong>Region:</strong> {recommendation["region"]}
        </div>
        <div class="recommendation-subtitle">Estimates</div>
        <div class="recommendation-detail">
            <strong>Estimated Cost:</strong> ${recommendation["estimated_cost"]}/hour<br/>
            <strong>Estimated Time:</strong> {recommendation["estimated_time"]}
        </div>
    </div>
    """
    return html

def animate_thinking_sequence():
    """
    Create a thinking animation before showing results
    
    Returns:
        None
    """
    thinking_container = st.empty()
    
    thinking_steps = [
        "🧠 Processing workload characteristics",
        "🧠 Processing workload characteristics.",
        "🧠 Processing workload characteristics..",
        "🧠 Processing workload characteristics...",
        "💭 Analyzing resource requirements",
        "💭 Analyzing resource requirements.",
        "💭 Analyzing resource requirements..",
        "💭 Analyzing resource requirements...",
        "⚙️ Optimizing configuration",
        "⚙️ Optimizing configuration.",
        "⚙️ Optimizing configuration..",
        "⚙️ Optimizing configuration...",
        "✨ Finalizing recommendation",
        "✨ Finalizing recommendation.",
        "✨ Finalizing recommendation..",
        "✨ Finalizing recommendation..."
    ]
    
    for step in thinking_steps:
        thinking_container.markdown(f"<div style='text-align: center; font-family: monospace; font-size: 18px; color: #6200ea;'>{step}</div>", unsafe_allow_html=True)
        time.sleep(0.2)
    
    thinking_container.empty()