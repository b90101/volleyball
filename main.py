from fastapi import *
from fastapi.responses import JSONResponse,HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List
import asyncio

from utils import security
from routers import user_router , team_router 
from models.user import UserRegister , UserLogin , UserUpdate
from models.team import TeamRegister

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
async def user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
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

@app.patch("/user")
async def update_user(user_update: UserUpdate, authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    payload = security.verify_jwt(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
    result = user_router.update(payload=payload,update_data=user_update)
    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=400, content=result)
    
@app.post("/create_team")
async def create_team(register_data: TeamRegister , authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    payload = security.verify_jwt(authorization[7:])
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    result = team_router.register(payload=payload,register_data=register_data)
    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=400, content=result)
    
@app.post("/teams/{team_id}/members")
async def add_team_members(team_id: int,user_ids: List[int] = Body(..., embed=True),authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization[7:]
    payload = security.verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    
    result = team_router.add_team_members(team_id=team_id, user_ids=user_ids, payload=payload)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

    
if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

