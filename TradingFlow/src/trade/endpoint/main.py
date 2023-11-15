from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

app = FastAPI()

from src.Agent import Agent
import uvicorn
runing_agent = None


class User(BaseModel):
    username: str
    password: str

# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}




@app.get("/")
def ping(Authorize: AuthJWT = Depends()):
    global runing_agent

    c_state = (
        runing_agent.env_vector.iloc[::-1][:10].to_dict("records")
        if runing_agent.predicted_action is not None
        else "-"
    )
    c_timestamp = (
        runing_agent.env_last_tick if runing_agent.predicted_action is not None else "-"
    )
    c_price = (
        runing_agent.env_last_price
        if runing_agent.predicted_action is not None
        else "-"
    )
    action = (
        runing_agent.predicted_action.item()
        if runing_agent.predicted_action is not None
        else "-"
    )

    command = (
        "Buy"
        if 1
        else "Sell"
        if 2
        else "Save"
        if runing_agent.predicted_action is not None
        else "-"
    )

    return {
        "message": "pong",
        "env": {
            "type": runing_agent.MODEL,
            "step": runing_agent.steps_done,
        },
        "predicted_action": {
            "action": action,
            "command": command,
            "at_time": c_timestamp,
            "at_price": c_price,
        },
        "state": {
            "candles": c_state,
        },
    }


def run(agent: Agent) -> None:
    global runing_agent
    runing_agent = agent
    uvicorn.run(app, host="0.0.0.0", port=8000)
