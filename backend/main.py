from fastapi import FastAPI


from routers.google import router as google_router
from routers.users import router as user_router

app = FastAPI()




app.include_router(google_router)
app.include_router(user_router)






