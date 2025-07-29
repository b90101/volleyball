from fastapi import FastAPI,File,Header,UploadFile,Form,Request,HTTPException,WebSocket,BackgroundTasks
from fastapi.responses import JSONResponse,HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List
import asyncio


from routers import user_router
from models.user import UserRegister

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
    user_router.print_all_users()
    return JSONResponse(
        {
            'hello':'hello world'
        }
    )


@app.post("/register")
async def register(name: str = Form(...),email: str = Form(...),password: str = Form(...)):
    user = UserRegister(name=name, email=email, password=password)
    result = user_router.register(user)

    if result["success"]:
        return JSONResponse(status_code=200, content=result)
    else:
        return JSONResponse(status_code=400, content=result)




if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

