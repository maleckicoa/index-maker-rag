

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

    /* Left Panel - Width */
    [data-testid="stSidebar"] {
        min-width: 400px;  /* Set the minimum width */
        max-width: 600px;  /* Set the maximum width */
    }
    [data-testid="stSidebarContent"] {
        padding: 10px;  /* Optional: Add some padding for better styling */
    }
    </style>
    """