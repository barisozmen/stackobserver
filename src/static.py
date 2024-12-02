scrollbar_style = """

    /* Targeting WebKit Browsers (Chrome, Safari) */
    ::-webkit-scrollbar {
        width: 45px; /* Width of the vertical scrollbar */
        height: 45px; /* Height of the horizontal scrollbar, if needed */
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1; /* Color of the scrollbar track */
        border-radius: 10px; /* Optional: Rounding the edges */
    }
    ::-webkit-scrollbar-thumb {
        background-color: #888; /* The scrollbar thumb color */
        border-radius: 10px; /* Optional: Rounding the edges */
        border: 4px solid #f1f1f1; /* Adding padding and color to increase visibility */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555; /* Color change on hover to increase visibility */
    }
    
"""