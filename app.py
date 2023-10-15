from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from stage import return_text

app = FastAPI()

origins = [
    "https://prts.wiki"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": True, "message": "Hello!"}


@app.post("/main")
async def main(pagetext: str = Form()):
    return await return_text(pagetext=pagetext)


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
