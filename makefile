.PHONY: st uvi uvi_reload scheduler


st:
	poetry run streamlit run chatbot_frontend/main.py \
	  --server.baseUrlPath /demo-apps/index-maker-rag \
	  --server.port 8501
  
uvi:
	PYTHONPATH=chatbot_api/src poetry run uvicorn main:app --host 0.0.0.0 --port 8080

uvi_reload:
	PYTHONPATH=chatbot_api/src poetry run uvicorn main:app --host 0.0.0.0 --port 8080 --reload 

neo4j_fresh:
	PYTHONPATH=. poetry run python -m index_maker.neo4j_fresh
