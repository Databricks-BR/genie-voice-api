from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from pyspark.sql.types import *
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from utils.genie_api import GenieAPI
from utils.agent_api import AgentAPI

import os
import asyncio
import re
import mlflow
import base64
import io
import pandas as pd

workspace_url = os.getenv('DATABRICKS_HOST')

app = FastAPI()

class ChatRequestText(BaseModel):
     token: str
     space_id: str
     keywords_genie: str
     conversation_id: str
     text: str
     chat_history: list

class ChatRequestAudio(BaseModel):
     audio: str
     chat_history: list

workspace_client = WorkspaceClient()

def transcribe_audio(audio_data):
    response = workspace_client.serving_endpoints.query(
        name="whisper_large_v3_endpoint",
        inputs=[audio_data]
    )
    return response.predictions[0]
    
def check_keywords(keywords, message):
    keywords = keywords.split(",")
    for keyword in keywords:
        if re.search(keyword, message, re.IGNORECASE):
            return (message)
    return None

def call_agent_model(token, message):   
    if len(message.strip()) == 0:
        return "ERROR: The question should not be empty", None

    data = {
        "messages": [
            {
                "role": "user",
                "content": f"token = {token}\n message = {message}"
            }
        ]
    }  

    df = pd.DataFrame(data)
    agent_api = AgentAPI(token=token,workspace_url=os.getenv('DATABRICKS_HOST'),agent='open_finance_genai_agent')
    result = agent_api.score_agent_model(df)

    return "", result


@app.post("/chat/")
async def chat_endpoint(chat_request: ChatRequestText):
    token = chat_request.token
    space_id = chat_request.space_id
    keywords_genie = chat_request.keywords_genie
    conversation_id = chat_request.conversation_id
    text = chat_request.text
    chat_history = chat_request.chat_history

    keyword_response = check_keywords(keywords_genie, text)

    if keyword_response:
        genie_api = GenieAPI(token=token,workspace_url=os.getenv('DATABRICKS_HOST'), space_id=space_id)
        conversation_id, result = genie_api.send_message_to_genie(conversation_id, text)
        chat_history.append([text, result])
    else:
        error, result = call_agent_model(token, text)
        chat_history.append([text, result])

    return {"response": result, "suggestion": None, "chat_history": chat_history, "conversation_id": conversation_id}


@app.post("/chat_audio/")
async def chat_audio_endpoint(chat_request: ChatRequestAudio):
    audio = chat_request.audio
    chat_history = chat_request.chat_history

    audio_data = audio.split(",")[-1]
    transcription = transcribe_audio(audio_data)

    return {"response": transcription, "suggestion": None, "chat_history": transcription}

environment = os.getenv("ENV", "prod")

if environment == "prod":
    try:
        target_dir = "static"
        app.mount("/", StaticFiles(directory=target_dir, html=True), name="site")
    except:
        print('ERROR - static not found')
else:
    print("Local mode")
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])    
