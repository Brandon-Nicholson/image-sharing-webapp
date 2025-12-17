# Image Sharing Web App

A small full-stack image sharing app built with **FastAPI**, **SQLAlchemy (async)**, **FastAPI Users**, **ImageKit** and a **Streamlit** frontend.

---

## Tech Stack

**Backend**
- FastAPI
- SQLAlchemy (async)
- FastAPI Users (JWT auth)
- SQLite (async via aiosqlite)
- ImageKit (image storage)

**Frontend**
- Streamlit

**Tooling**
- Python 3.12
- Poetry for dependency and environment management

---

## Project Structure (high level)

image-sharing-webapp/
│
├── app/
│ ├── app.py # FastAPI routes
│ ├── db.py # Database models & session
│ ├── users.py # FastAPI Users setup
│ ├── images.py # ImageKit integration
│ └── schemas.py # Pydantic schemas
│
├── frontend.py # Streamlit UI
├── main.py # FastAPI entrypoint
├── test.db # SQLite database (generated)
├── pyproject.toml
└── README.md


---

## Setup

### 1. Install dependencies
Make sure you have **Poetry** installed, then from the project root:
```bash
poetry install
```

### 2. Create a .env file in the project root:
```bash
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL=https://ik.imagekit.io/your_id
```

### 3. Create the database
```bash
poetry run python -c "from app.db import create_db_and_tables; import asyncio; asyncio.run(create_db_and_tables())"
```

### 4. Start the FastAPI server
```bash
poetry run uvicorn main:app --reload --port 8000
```

### 5. Run the Streamlit frontend
```bash
poetry run streamlit run frontend.py
```

### Notes:

- Authentication is handled via JWT using FastAPI Users.
- Images are uploaded and stored via ImageKit, not locally.
- SQLite is used intentionally to keep setup simple.
- This project focuses on clean async patterns rather than production hardening.
