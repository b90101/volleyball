from fastapi import FastAPI,File,Header,UploadFile,Form,Request,HTTPException,WebSocket,BackgroundTasks
from fastapi.responses import JSONResponse,HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List
import asyncio

from utils import security
from routers import user_router
from models.user import UserRegister , UserLogin

app = FastAPI()

#避免CORS設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#預設首頁
@app.get("/")
async def fun():
    return JSONResponse(
        {
            'hello':'hello world'
        }
    )


@app.post("/register")
async def register(register_data: UserRegister):
    result = user_router.register(register_data)

    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=400, content=result)

@app.post("/login")
async def login(login_data: UserLogin):
    result = user_router.login(login_data)
    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=400, content=result)


@app.get("/user")
async def user(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = authorization[7:]  # 去掉 "Bearer "
    payload = security.verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "user_id": payload["user_id"],
        "username": payload["username"],
        "email": payload["email"],
    }


    
if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

