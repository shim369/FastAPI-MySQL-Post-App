from fastapi import FastAPI, HTTPException, Depends, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def read_root(request: Request, db: db_dependency):
    posts = db.query(models.Post).all()
    context = {"request": request, "posts": posts, "title": "FastAPI MySQL App"}
    return templates.TemplateResponse("index.html", context)

@app.get("/add_post", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def add_post_form(request: Request):
    context = {"request": request, "title": "Add Post | FastAPI MySQL App"}
    return templates.TemplateResponse("add.html", context)

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/posts/{post_id}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency, request: Request):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post was not found')
    context = {"request": request, "post": post, "title": "Edit | FastAPI MySQL App"}
    return templates.TemplateResponse("edit.html", context)


@app.post("/posts/{post_id}/update", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int, 
    title: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(get_db)
):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not found')

    db_post.title = title
    db_post.url = url
    db.commit()
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404,detail='Post not found')
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}