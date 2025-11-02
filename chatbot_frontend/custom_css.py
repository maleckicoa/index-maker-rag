

import streamlit as st

def get_css():
    return"""
    <style>

    /* ChatInput - THE TEXT WINDOW IN THE RIGHT PANEL */
    
    div.stChatInput:focus-within *,
    div.stChatInput *:focus {
        outline: none !important;
        box-shadow: none !important; /* Removes inner border effect */
        border-color: transparent !important;
    }

    div.stChatInput {
        border: 2px solid transparent !important; /* No border when not focused */
        border-radius: 20px !important;
        transition: border 0.2s ease-in-out;
    }

    div.stChatInput:focus-within {
        border: 2px solid #3498db !important; /* Blue border appears on focus */
        border-radius: 20px !important;
    }


    /* The most upper line in the right panel (not really visible) - Border color and width */
    div[data-testid="stDecoration"] {
        background: #DDEAF6 !important;  /* Change to your preferred color */
        height: 2px !important;  /* Adjust thickness */
    }

    /* Change Sidebar width */
    [data-testid="stWidgetLabel "] {
        max-height: 0px !important; /* Adjust as needed */
        margin: 0 auto; /* Center the header */
    }

    /* Code Blocks - Container height and Scrolling */
    .stCode {
        max-height: 200px; /* Set desired height */
        overflow-y: auto !important; /* Force vertical scrolling */
    }

    /* Code Blocks - Font size and family */
    code {
        font-size: 14px !important; /* Fix font size for code blocks */
        font-family: 'Menlo' !important; /* Fix font family for code blocks Arial Consolas Monaco */
    }

    /* Left Panel - Width (Desktop) - Ensure it's open by default */
    [data-testid="stSidebar"] {
        min-width: 400px;  /* Set the minimum width */
        max-width: 600px;  /* Set the maximum width */
    }
    
    /* Force sidebar to be visible/open on desktop */
    @media (min-width: 768px) {
        [data-testid="stSidebar"] {
            display: block !important;
            transform: translateX(0) !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="false"] {
            display: block !important;
            transform: translateX(0) !important;
        }
    }
    [data-testid="stSidebarContent"] {
        padding: 10px;  /* Optional: Add some padding for better styling */
    }

    /* Mobile Responsive Styles */
    @media (max-width: 767px) {
        /* Sidebar: Full width on mobile when opened, hidden when collapsed */
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-100%) !important;
        }
        
        /* Ensure main content takes full width on mobile */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
            margin-left: 0 !important;
        }
        
        /* Fix title position - prevent movement */
        div[data-testid="column"] {
            flex-shrink: 0 !important;
        }
        
        /* Charts/graphs: Responsive width, right padding, and shorter height on mobile */
        [data-testid="stVegaLiteChart"],
        [data-testid="stLineChart"],
        div[data-testid="stVegaLiteChart"] > div {
            width: 100% !important;
            max-width: 100% !important;
            padding-right: 1.5rem !important;
        }
        
        /* Make chart less tall on mobile only */
        [data-testid="stVegaLiteChart"],
        [data-testid="stVegaLiteChart"] > div {
            max-height: 250px !important;
            overflow: hidden !important;
        }
        
        /* Target SVG elements inside charts to constrain height */
        [data-testid="stVegaLiteChart"] svg {
            height: 250px !important;
            max-height: 250px !important;
            width: 100% !important;
        }
        
        /* Target chart containers */
        .element-container:has([data-testid="stVegaLiteChart"]) {
            max-height: 250px !important;
            overflow: hidden !important;
        }
        
        /* Dataframes: Horizontal scroll on mobile */
        [data-testid="stDataFrame"] {
            overflow-x: auto !important;
            width: 100% !important;
        }
    }
    </style>
    """