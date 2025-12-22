from fastapi import FastAPI
from .schema import LoginSchema, SignUpSchema
from .auth import signup_users as auth_signup_users, signup_staffs as auth_signup_staffs, login_staffs as auth_login_staffs, login_users as auth_login_users

app = FastAPI()

@app.post('/signup/users')
async def signup_users(user_data: SignUpSchema):
    return await auth_signup_users(user_data)

@app.post('/login/users')
async def login_users(user_data: LoginSchema):
    return await auth_login_users(user_data)

@app.post('/signup/staffs')
async def signup_staffs(user_data: SignUpSchema):
    return await auth_signup_staffs(user_data)

@app.post('/login/staffs')
async def login_staffs(user_data: LoginSchema):
    return await auth_login_staffs(user_data)


