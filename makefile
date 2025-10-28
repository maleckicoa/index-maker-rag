.PHONY: st uvi guni


st:
	poetry run streamlit run chatbot_frontend/main.py \
	  --server.baseUrlPath /demo-apps/index-maker-rag \
	  --server.port 8501
  
uvi:
	PYTHONPATH=chatbot_api/src poetry run uvicorn main:app --host 0.0.0.0 --port 8080

uvi_reload:
	PYTHONPATH=chatbot_api/src poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload --reload-dir /Users/aleksamihajlovic/Documents/index-maker-rag

guni:
	PYTHONPATH=chatbot_api/src poetry run gunicorn main:app \
	    -k uvicorn.workers.UvicornWorker \
	    --bind 0.0.0.0:8080 \
	    --workers 3 \
	    --timeout 52 \
	    --reload

 
