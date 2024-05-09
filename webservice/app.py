import boto3
from botocore.config import Config
import os
from dotenv import load_dotenv
from typing import Union
import logging
from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid
from boto3.dynamodb.conditions import Key
from getSignedUrl import getSignedUrl

load_dotenv()

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logger.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Post(BaseModel):
    title: str
    body: str


my_config = Config(
    region_name='us-east-1',
    signature_version='v4',
)

dynamodb = boto3.resource('dynamodb', config=my_config)
table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))
s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
bucket = os.getenv("BUCKET")


@app.post("/posts")
async def post_a_post(post: Post, authorization: str | None = Header(default=None)):

    logger.info(f"title : {post.title}")
    logger.info(f"body : {post.body}")
    logger.info(f"user : {authorization}")

    # Doit retourner le résultat de la requête la table dynamodb
    #assert post.title, "Veuillez insérer un titre"
    #assert post.body, "Veuillez insérer un contenu"
    #assert authorization, "Vous devez être connecté pour publier"

    post_id = uuid.uuid4()

    post_json = {
        "user": f"USER#{authorization}",
        "id": f"POST#{post_id}",
        "title": f"{post.title}",
        "body": f"{post.body}",
    }

    data = table.put_item(Item=post_json)

    return data

@app.get("/posts")
async def get_all_posts(user: Union[str, None] = None):

    liste_posts = []
    if user:
        response = table.query(
            Select='ALL_ATTRIBUTES',
            KeyConditionExpression=Key('user').eq(f"USER#{user}")
        )
        for item in response['Items']:
            liste_posts.append(item)
    else:
        response = table.scan(
            Select='ALL_ATTRIBUTES',
        )
        for item in response['Items']:
            liste_posts.append(item)

    # Doit retourner une liste de post
    return liste_posts


@app.delete("/posts/{post_id}")
async def get_post_user_id(post_id: str):
    # Doit retourner le résultat de la requête la table dynamodb
    return []

@app.get("/signedUrlPut")
async def get_signed_url_put(filename: str,filetype: str, postId: str,authorization: str | None = Header(default=None)):
    return getSignedUrl(filename, filetype, postId, authorization)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

