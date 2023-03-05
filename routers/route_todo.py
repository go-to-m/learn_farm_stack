from fastapi import APIRouter
from fastapi import Response, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from database import db_create_todo, db_get_todo,  db_get_single_todo, db_update_todo, db_delete_todo
from schemas import *
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrf

router = APIRouter()
auth = AuthJwtCsrf()

@router.post("/api/todo", response_model=Todo)
async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = await auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(status_code=404, detail="Create task failed")

@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request, response: Response):
    # auth.verify_jwt(request)
    res = await db_get_todo()
    return res

@router.get("/api/todo/{id}", response_model=Todo)
async def get_single_todo(id: str, request: Request, response: Response):
    new_token, _ = auth.verify_jwt(request)
    res = await db_get_single_todo(id)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"Task of ID:{id} does not exist")

@router.put("/api/todo/{id}", response_model=Todo)
async def update_todo(id: str, data: TodoBody, request: Request, response: Response, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, todo)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"update tast failed")

@router.delete("/api/todo/{id}")
async def delete_todo(id: str, request: Request, response: Response, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(request, csrf_protect, request.headers)
    res = await db_delete_todo(id)
    response.set_cookie(key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return {"message": "Successfully deleted"}
    raise HTTPException(status_code=404, detail=f"delete task failed")