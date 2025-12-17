import uuid
from typing import Optional, Sequence
from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# load environment variables
SECRET = os.environ["SECRET_KEY"]

# user manager
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    # on after register
    async def on_after_register(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has registered.") 
    # on after update
    async def on_after_update(self, user: User, updated_fields: Sequence[str], request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has updated their fields: {updated_fields}")   
    # on after delete
    async def on_after_delete(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None ):
        print(f"User {user.id} has deleted their account.")   
    # on after login
    async def on_after_login(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has logged in.")
    # on after verify
    async def on_after_verify(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has verified their account.")  
    # on after reset password
    async def on_after_reset_password(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has reset their password.")  
    # on after reset password request
    async def on_after_reset_password_request(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has requested a password reset.")
    # on after request verify
    async def on_after_request_verify(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has requested a verification email.")
    # on after update password
    async def on_after_update_password(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has updated their password.")
    # on after update email
    async def on_after_update_email(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has updated their email.")
    # on after update username
    async def on_after_update_username(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has updated their username.")
    # on after update email request
    async def on_after_update_email_request(self, user: User, request: Optional[Request] = None, response: Optional[Response] = None):
        print(f"User {user.id} has requested a email update.")
   
# get user manager
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
    
# bearer transport
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# get jwt strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# fastapi users
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# current active user
current_active_user = fastapi_users.current_user(active=True)

 