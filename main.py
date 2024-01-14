import os
import time
import uvicorn

from requests import Session
from requests.adapters import HTTPAdapter, Retry
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv


load_dotenv()
marino = os.getenv("MARINO_URL", 'http://0.0.0.0:12345')
marino_id = os.getenv("MARINO_ID", '')
marino_token = os.getenv("MARINO_TOKEN", '')
chatwoot = os.getenv("CHATWOOT_URL", 'http://localhost:3000')
chatwoot_token = os.getenv("CHATWOOT_TOKEN", '')

retries = Retry(
  total=5, backoff_factor=1, status_forcelist=[502, 503, 504]
)
session = Session()  # reuse tcp connection
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

app = FastAPI(
    title='Chatwoot proxy server',
    Description="Chatwoot proxy server for marino",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


# other format, see: https://www.chatwoot.com/docs/product/others/interactive-messages
def send_to_bot(message, sender, user):
    data = {
            "conversation": str(sender),
            "prompt": message,
            "user": str(user)
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {marino_token}"
    }
    r = session.post(f'{marino}/v1/chat/{marino_id}',json=data, headers=headers)
    res = r.json()
    return res['choices'][0]['message']['content']

def send_to_chatwoot(account, conversation, message):
    data = {
        'content': message
    }
    url = f"{chatwoot}/api/v1/accounts/{account}/conversations/{conversation}/messages"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api_access_token": f"{chatwoot_token}"
    }
    r = session.post(url, json=data, headers=headers)
    return r.json()


@app.on_event("startup")
async def startup():
    logger.info("Server started")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Server shutdown")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(request, exception):
    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(exception.detail)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "errcode": 422,
            "msg": "request validation error",
            "detail" : exc.errors(),
            "body": exc.body}),
    )


@app.get('/')
async def index():
    return {"message": "index", "code": 0}

@app.post('/bot/chat')
async def chat(request: Request):
    try:
        data = await request.json()
        message_type = data['message_type']
        message = data['content']
        conversation = data['conversation']['id']
        contact = data['sender']['id']
        account = data['account']['id']
        if(message_type == "incoming"):
            bot_response = send_to_bot(message, account, contact)
            create_message = send_to_chatwoot(account, conversation, bot_response)
            logger.info(f'send message: {create_message["content"]} from {data["account"]["name"]} which id is {account}')
            return create_message
    except Exception as e:
        logger.error(e)
        return {"code": 500, "message": "Server exception error"}, status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    port = int(os.getenv("PORT") or 8000)
    uvicorn.run(app=app, host='0.0.0.0', port=port)