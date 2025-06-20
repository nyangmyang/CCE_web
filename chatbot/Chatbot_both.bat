@echo off
start cmd /k "streamlit run Chatbot_app.py --server.port 8502 --server.headless true"
start cmd /k "streamlit run Chatbot_stock_expert_html.py --server.port 8501"