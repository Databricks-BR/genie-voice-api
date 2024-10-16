# Databricks notebook source
!pip install -r ./requirements.txt
!pip install --upgrade typing-extensions
dbutils.library.restartPython()

# COMMAND ----------

#%%writefile ./_resources/genie_api.py
import requests
import json
import pandas as pd
import time
from tabulate import tabulate
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

workspace_client = WorkspaceClient()

class GenieAPI:

    def __init__(self, token, space_id):
        self.__token = token
        self.space_id = space_id
        self.__base_url = f"https://e2-demo-field-eng.cloud.databricks.com/api/2.0/genie/spaces/{self.space_id}"
        self.__headers = {
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json"
        }

    def start_conversation(self, content):
        resp = requests.post(
            f"{self.__base_url}/start-conversation", 
            json={"content": content},
            headers=self.__headers
        )
        resp.raise_for_status()
        return resp.json()
    
    def create_message(self, conversation_id, content):
        resp = requests.post(
            f"{self.__base_url}/conversations/{conversation_id}/messages",
            json={"content": content},
            headers=self.__headers
        )
        resp.raise_for_status()
        return resp.json()

    def poll_query_results(self, conversation_id, message_id):
        while True:
            resp = requests.get(f"{self.__base_url}/conversations/{conversation_id}/messages/{message_id}/query-result",headers=self.__headers)
            resp.raise_for_status()
            resp = resp.json()['statement_response']
                            
            state = resp['status']['state']
            
            if state == 'SUCCEEDED':
                data = resp['result']
                meta = resp['manifest']
                rows = [[c['str'] for c in r['values']] for r in data['data_typed_array']]
                columns = [c['name'] for c in meta['schema']['columns']]
                df = pd.DataFrame(rows, columns=columns)

                if len(df.columns) > 1:
                    df = tabulate(df, headers='keys', tablefmt='html')
                    return df
                else:
                    text = df.to_string(index=False)
                    #print("Passo 6: " + text)
                    return text

            elif state == 'RUNNING' or state == 'PENDING':
                #print("Passo 7: " + state)
                time.sleep(5)            
            else:
                #print(" Nao achou nada")
                return None
                  
    def poll_for_result(self, conversation_id, message_id):
        #print("entrou aqui")
        while True:
            resp = requests.get(f"{self.__base_url}/conversations/{conversation_id}/messages/{message_id}", headers=self.__headers)
            resp.raise_for_status()
            resp = resp.json()
            #print("Passo 1: " + resp['status'])
            if resp['status'] == "EXECUTING_QUERY":
                sql = next((r for r in resp['attachments'] if 'query' in r), {}).get('query', {}).get('content', 'Result not found sql')
                if sql:
                    return self.poll_query_results(conversation_id, message_id)
                
                #print("Passo 2: " + resp['status'])
                return None
            elif resp['status'] in ('SUBMITTED', 'FILTERING_CONTEXT', 'ASKING_AI'):
                #print("Passo 3: " + resp['status'])
                time.sleep(5)
            elif resp['status'] == 'COMPLETED':
                #print("Passo 4: " + resp['status'])
                return next((r for r in resp['attachments'] if 'text' in r), {}).get('text', {}).get('content', 'Result not found')
            else:
                time.sleep(5)
                #print("Passo 5: ")
                #return None
      
    def send_message_to_genie(self, conversation_id, message):    

        if conversation_id == "0":            
            start_resp = self.start_conversation(message)
            conversation_id = start_resp['conversation_id']
            message_id = start_resp['message_id']
        else:
            create_message_resp = self.create_message(conversation_id, message)                        
            conversation_id = create_message_resp['conversation_id']
            message_id = create_message_resp['id']
        
        result = self.poll_for_result(conversation_id, message_id)

        if result:
            #print("Passo 10: " + result)
            result_formatted = self.query_model_format(result)
        else:
            #print("Passo 11")
            result_formatted = "Result not found in Genie"

        return conversation_id, result_formatted
        
    def query_model_format(self, text_to_format):
        w = WorkspaceClient()
       
        prompt = "answer using bullets and sub-bullets. Format the message in a clear and organized way. Short answer. Do not need to show the prompt information as \"Here is a summary of the data in a clear and organized way\". Do not show SQL instructions to user. Answer always in English"

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            { 
                "role": "user", 
                "content": text_to_format 
            }
        ]

        messages = [ChatMessage.from_dict(message) for message in messages]
        response = w.serving_endpoints.query(
            name="databricks-meta-llama-3-1-405b-instruct",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content 


# COMMAND ----------

#%%writefile ./_resources/agent_api.py
import requests
import json
import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

workspace_client = WorkspaceClient()

class AgentAPI:

    def __init__(self, token):
        self.__base_url = "https://e2-demo-field-eng.cloud.databricks.com/serving-endpoints/open_finance_agent_endpoint"
        self.__headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
   
    def create_tf_serving_json(self, data):
        if isinstance(data, pd.DataFrame):
            return {'inputs': data.to_dict(orient='list')}
        elif isinstance(data, dict):
            return {'inputs': {name: data[name] if isinstance(data[name], list) else [data[name]] for name in data.keys()}}
        else:
            return {'inputs': data.tolist() if hasattr(data, 'tolist') else data}

    def score_agent_model(self, dataset):
        url = f'{self.__base_url}/invocations'
        
        ds_dict = self.create_tf_serving_json(dataset)
        data_json = json.dumps(ds_dict, allow_nan=True)    
        
        response = requests.request(method='POST', headers=self.__headers, url=url, data=data_json)

        result_formatted = self.query_model_format(response.text)
        return result_formatted

    def query_model_format(self, message):
        w = WorkspaceClient()

        prompt = "Only show to the user the Result section. Make sure never show Predictions, Function Call, Token or Short Description to the user. Format the Result message in a clear and organized way. Do not need to show Result title. Answer always in English"

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            { 
                "role": "user", 
                "content": message 
            }
        ]
        messages = [ChatMessage.from_dict(message) for message in messages]
        response = w.serving_endpoints.query(
            name="databricks-meta-llama-3-1-405b-instruct",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content   

# COMMAND ----------

#%%writefile ./app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from pyspark.sql.types import *
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from _resources.tracker import Tracker
from _resources.conversation import keyword_responses
#from _resources.genie_api import GenieAPI
#from _resources.agent_api import AgentAPI

import os
import asyncio
import re
import mlflow
import base64
import io
import pandas as pd

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
        return "ERROR: The question should not be empty"

    data = {
        "messages": [
            {
            "role": "user",
            "content": f"""                    
                    token = {token}
                    message = {message}                    
                    """  
            }
        ]
    }  

    df = pd.DataFrame(data)
    agent_api = AgentAPI(token)
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
        genie_api = GenieAPI(token, space_id)
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


@app.get("/tracker")
async def get_tracker(request: Request):
    if environment == "dev":
        email = "dev"
        org = "local"
    else:
        org = WorkspaceClient().get_workspace_id()
        email = request.headers.get('X-Forwarded-Email')
    Tracker().track_app_user(email, org, 'open-finance')
    return {"email": email}


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


# COMMAND ----------

chat_request = ChatRequestText(
    token="<put your token here>",
    space_id="<put your genie space id here>",
    keywords_genie="<put your genie keywords here>",
    conversation_id="0",
    text="What is Open Finance?",
    chat_history=[]
)

response = await chat_endpoint(chat_request)
display(response)

# COMMAND ----------

chat_request = ChatRequestText(
    token="<put your token here>",
    space_id="<put your genie space id here>",
    keywords_genie="<put your genie keywords here>",
    conversation_id="0",
    text="In how many banks does R2-D2 operate? Bring the names.",
    chat_history=[]
)

response = await chat_endpoint(chat_request)
display(response)

# COMMAND ----------

# MAGIC %md
# MAGIC