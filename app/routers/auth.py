from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import oauth2
from .. import database, schemas, models, utils, oauth2
router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin ,db: Session = Depends(database.get_db)):

    condition = models.User.email == user_credentials.username if '@' in user_credentials.username else models.User.username == user_credentials.username
    
    user = db.query(models.User).filter(condition).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = 'Invalid Credentials')
    
    if not utils.verify(user_credentials.password, user.password):  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = 'Invalid Credentials')
    
    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return access_token

