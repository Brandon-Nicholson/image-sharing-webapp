from fastapi import FastAPI, HTTPException, UploadFile, Form, Depends, File
from app.schemas import PostCreate
from app.db import Post, create_db_and_tables, get_async_session, User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from app.users import current_active_user, auth_backend, fastapi_users
from app.schemas import UserRead, UserCreate, UserUpdate
from app.db import User
from fastapi import Depends
# lifespan for the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

# app instance
app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

# upload post endpoint
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    
    # check if the file is an image
    temp_file_path = None
    try: # create a temporary file to store the file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            
        # upload the file to imagekit
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )
        if upload_result.response_metadata.http_status_code == 200:
            
            # create a new post
            post = Post(
                caption=caption,
                user_id=user.id,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )

            # add the post to the session
            session.add(post)
            # commit the session
            await session.commit()
            await session.refresh(post)
            return post
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()
    
# get feed endpoint
@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    # get all posts ordered by created_at descending
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    users_dict = {user.id: user.email for user in users}
    
    # convert posts to a list of dictionaries
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": users_dict.get(post.user_id, None)
            }
        )
    return {"posts": posts_data}

# delete post endpoint
@app.delete("/posts/{post_id}")
async def delete_post(
                      post_id: str, 
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(current_active_user)
                      ):
    try: # get the post by id
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).filter(Post.id == post_uuid))
        post = result.scalars().first()
        # check if the post exists
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        # check if the user is the owner of the post
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this post")
        # delete the post
        await session.delete(post)
        # commit the session
        await session.commit()
        # return the message
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# dummy posts for testing
text_posts = {
    1: {
        "title": "First Coffee of the Day",
        "content": "Nothing beats that first sip of coffee while watching the city wake up. Small rituals make the mornings better."
    },
    2: {
        "title": "Late Night Coding",
        "content": "Another night lost in code. It’s crazy how time disappears when you’re deep in a problem that finally starts to click."
    },
    3: {
        "title": "Gym Progress",
        "content": "Feeling stronger every week. Consistency really is the secret sauce — no shortcuts, just showing up."
    },
    4: {
        "title": "Sunset Reset",
        "content": "Stopped what I was doing to catch the sunset tonight. Reminded me that slowing down is just as important as grinding."
    },
    5: {
        "title": "Trying Something New",
        "content": "Said yes to something I would’ve normally avoided. Growth almost always starts outside the comfort zone."
    },
    6: {
        "title": "Good Playlist Day",
        "content": "You know it’s a good day when your playlist hits nonstop from start to finish."
    },
    7: {
        "title": "Deep Thoughts",
        "content": "Wild how a simple walk can turn into a full existential spiral in the best way possible."
    },
    8: {
        "title": "Clean Eating Win",
        "content": "Kept it clean all day — steak, eggs, fruit, and plenty of water. Feels great not crashing anymore."
    },
    9: {
        "title": "Late Night Drive",
        "content": "Driving down PCH at night."
    },
    10: {
        "title": "Building the Future",
        "content": "Every small project feels like a brick laid toward something bigger. One day this grind is going to pay off."
    }
}

# get all posts endpoint
@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return list(text_posts.values())[:limit]
    
    return text_posts

# get post by id endpoint
@app.get("/posts{id}")
def get_post(id: int):
    
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return text_posts.get(id)

# create post endpoint
@app.post("/posts")
def create_post(post: PostCreate) -> PostCreate:
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys())+1] = new_post
    return new_post

