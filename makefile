.PHONY: st uvi guni

st:
	streamlit run chatbot_frontend/main.py
uvi:
	PYTHONPATH=chatbot_api/src uvicorn main:app --host 0.0.0.0 --port 800

uvi_reload:
	PYTHONPATH=chatbot_api/src uvicorn main:app --host 0.0.0.0 --port 800 --reload --reload-dir /Users/aleksamihajlovic/Documents/

guni:
	PYTHONPATH=chatbot_api/src gunicorn main:app \
	    -k uvicorn.workers.UvicornWorker \
	    --bind 0.0.0.0:800 \
	    --workers 3 \
	    --timeout 52 \
	    --reload

 
