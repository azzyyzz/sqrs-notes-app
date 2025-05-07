# Notes app

Python app to keep track of your notes. You can also translate your English notes to Russian.

## Install dependencies and run

1. `pip install poetry`
2. `poetry install`
3. `poetry run uvicorn backend.app.main:app --reload` - Run backend
4. `poetry run streamlit run frontend/app.py` - Run frontend
