"""
Entry point to run the Dairy App backend.
Run with: uvicorn main:app --reload
"""
from main import app
from config.settings import settings

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
