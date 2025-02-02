from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database.database import SessionLocal
from app.model.models import User
from app.schemas.schemas import UserCreate
from app.services.user_service import UserService
from app.services.news_service import NewsService

templates = Jinja2Templates(directory="templates")
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to check if user is logged in
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = UserService.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create a UserCreate object manually
    user_create = UserCreate(username=username, email=email, password=password)

    # Call the UserService to create the user
    UserService.create_user(user_create, db)

    # Redirect to the login page
    return RedirectResponse("/", status_code=303)

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = UserService.authenticate_user(username, password, db)
    if user:
        request.session["user_id"] = user.user_id
        return RedirectResponse("/users/chatbot", status_code=303)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@router.get("/chatbot")
def chatbot_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_history = NewsService.get_summarized_articles(user.user_id, db)
    return templates.TemplateResponse(
        "chatbot.html",
        {"request": request, "user": user, "history": user_history},
    )
