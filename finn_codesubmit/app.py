from fastapi import FastAPI

from finn_codesubmit import router


app = FastAPI()
app.include_router(router.router)
