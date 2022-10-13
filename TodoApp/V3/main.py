from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos, users
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# If you need to have two independent FastAPI applications,
# with their own independent OpenAPI and their own docs UIs,
# you can have a main app and "mount" one (or more) sub-application(s).
# "Mounting" means adding a completely "independent" application in a specific path,
# that then takes care of handling everything under that path,
# with the path operations declared in that sub-application.
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
