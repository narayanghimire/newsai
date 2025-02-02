import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from app.database.database import engine, Base
from routers.user_router import router as user_router
from routers.news_router import router as news_router
import uvicorn

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
# Initialize FastAPI
app = FastAPI()


app.add_middleware(SessionMiddleware, secret_key=secret_key)
# Create the database tables
Base.metadata.create_all(bind=engine)

# Mount static files for CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(news_router, prefix="/news", tags=["News"])


# Serve the index.html as the default route
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)
