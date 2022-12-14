from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, requests, Response, status, HTTPException, Depends, APIRouter
from ..database import engine, get_db 
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional, List
from pydantic import parse_obj_as
from sqlalchemy import  or_
import math
from sqlalchemy import func
router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user:schemas.UserIn, db: Session = Depends(get_db)):

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    user.first_name = user.first_name.capitalize()
    user.last_name = user.last_name.capitalize()
    new_user = models.User(**user.dict())

    user = db.query(models.User)

    formErrors = []
    if user.filter(models.User.email==new_user.email).first():
        formErrors.append(f"Email {new_user.email} already exists.")
    if user.filter(models.User.username==new_user.username).first():
        formErrors.append(f"Username {new_user.username} already exists.")
    
    if len(formErrors) == 0:
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail = "Something went wrong.")
        return new_user
    else:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content = {"detail": formErrors}
        )



@router.get("/get-logged-in-user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def get_logged_in_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id==current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id: {id} was not found')
    return user

@router.put("/update-logged-in-user")
def update_logged_in_user(user: schemas.UserUpdate,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    updated_user = db.query(models.User).filter(models.User.id == current_user.id)


    if updated_user.first() == None:
        return JSONResponse(
        status_code = status.HTTP_404_NOT_FOUND,
        content= {"detail":f"user with id: {current_user.id} does not exists!"}
    )
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exists!")
    if updated_user.first().id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not authorized to perform requested action")
    
    user_update = updated_user.first()
    
    if user.email:
        user_update.email = user.email
    if user.first_name:
        user_update.first_name= user.first_name
    if user.last_name:
        user_update.last_name = user.last_name
    if user.phone_number:
        user_update.phone_number = user.phone_number
        
    # updated_user.update(user_update, synchronize_session=False)
    db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= schemas.UserOut(**jsonable_encoder(updated_user.first())).dict()
    )
    
@router.get("/get-users")
def get_users(
        db: Session = Depends(get_db),  
        current_user: int = Depends(oauth2.get_current_user),
        limit:int=10, 
        page:int=1,
        search:Optional[str]=""
        ):
    
    if page<=0:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'detail' : 'Invalid page value.'
            }
            )
    
    
    
    condition = or_(
        models.User.email.ilike(f'%{search}%'), 
        models.User.phone_number.ilike(f'%{search}%'),
        models.User.first_name.ilike(f'%{search}%'),
        models.User.last_name.ilike(f'%{search}%'),
        )
    
    users = db.query(models.User).order_by(models.User.created_at.asc()).filter(condition)
    total_result = len(users.all())
    
    def query(page, result):
        if len(result) == 0:
            return {"page": 1, "result": users.limit(limit).offset(0).all()}
        return {"page":page, "result": result}
    
    query_func = query(page, users.limit(limit).offset((page-1)*limit).all())
    current_page = query_func.get('page')
    query_result = query_func.get('result')
    query_result = parse_obj_as(List[schemas.UserOut], query_result)
    query_result = [user.dict() for user in query_result]
    
    response = {
        "data": query_result, 
        "pages": 1 if total_result >= 0 and total_result <= limit  else math.ceil(total_result/limit),
        "current_page": current_page,
        "total_result" : total_result,
        "result_count_per_page": limit,
        "query_result": len(query_result),
        "pagination": {}
        }
    
    if current_page > 1:
        response["pagination"]["previous"] = f"/users/get-users?page={current_page-1}&search={search}"
    else:
        response["pagination"]["previous"] = None
    
    if current_page == math.ceil(total_result/limit) or len(query_result) == 0:
        response["pagination"]["next"] = None
    else:
        response["pagination"]["next"] = f"/users/get-users?page={current_page+1}&search={search}"
   
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response
    )