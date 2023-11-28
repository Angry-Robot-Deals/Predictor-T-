import os

from dotenv import find_dotenv, load_dotenv

load_dotenv('../../.env')

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud
from .schemas import UserSchemaIn, UserSchemaOut
from .auth import create_access_token, verify_password, verify_token, check_active, check_admin
from .sendmail import send_mail

from .database import get_db, engine

from . import models

app = FastAPI()

from src.Agent import Agent

runing_agent = None
notify = False

@app.get("/ping")
def index():
    return {"message": "service running..."}


@app.get("/", dependencies=[Depends(check_active)])
def predict():
    global runing_agent
    if runing_agent is None:
        return {
            "agent": None,
        }

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


@app.post("/register")
def register_user(user: UserSchemaIn, db: Session = Depends(get_db)):
    db_user = crud.get_users_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="{user.username} - already registered")
    db_user = crud.create_user(db=db, user=user)
    token = create_access_token(db_user)
    if notify:
        send_mail(to=db_user.email, token=token, recipient=db_user.username)
    return db_user


@app.post("/login")
def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = crud.get_users_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=401, detail="Username not found. Please register first"
        )

    if verify_password(form_data.password, db_user.hashed_password):
        token = create_access_token(db_user)
        return {"access_token": token, "token_Type": "bearer"}
    raise HTTPException(status_code=401, detail="Check your username and password")


@app.get("/verify/{token}", response_class=HTMLResponse)
def login_user(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    username = payload.get("sub")
    db_user = crud.get_users_by_username(db, username)
    db_user.is_active = True
    db.commit()
    return f"""
    <html>
        <head>
            <title>Confirmation of Registration</title>
        </head>
        <body>
            <h2>Activation of {username} successful!</h2>
            <a href="https://localhost:8000">
                Zurück
            </a>
        </body>
    </html>
    """


@app.get("/users", dependencies=[Depends(check_admin)])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users


@app.get("/secured", dependencies=[Depends(check_admin)])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users


@app.get("/adminsonly", dependencies=[Depends(check_admin)])
def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_users(db=db)
    return users


def run(agent: Agent) -> None:
    global runing_agent
    import uvicorn
    runing_agent = agent
    uvicorn.run(app, host="0.0.0.0", port=8000)
