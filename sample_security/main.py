from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .security import create_access_token, create_refresh_token
import jwt
app = FastAPI()


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user (e.g. check the credentials in the database)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=timedelta(days=1)
    )
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.post("/refresh")
async def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        access_token = create_access_token(
            data={"sub": username}, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token}
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

