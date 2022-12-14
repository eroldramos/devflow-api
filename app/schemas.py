from pydantic import BaseModel, EmailStr, root_validator, validator
from datetime import datetime, timezone
from typing import Optional, List
from pydantic.types import conint
from .utils import date_beautifier
class UserIn(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    
    

class UserOut(BaseModel):
    id:int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str
    

    
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    created_at: datetime
    class Config:
        orm_mode = True

    @root_validator()
    def date_beautify(cls, values):
        return date_beautifier(values)
        
     
    
class UserPosts(UserOut):
    post : List[PostBase] = []
    total_posts : int = None
    class Config:
        orm_mode = True
        
    @root_validator()
    def total_posts(cls, values):
        values['total_posts'] = len(values.get('post'))
 
        return values
class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = True



class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int  
    user: UserOut

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expiry_date: datetime

class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)