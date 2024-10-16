import requests
import json
import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

workspace_client = WorkspaceClient()

class AgentAPI:

    def __init__(self, token, workspace_url,agent):
        self.__base_url = "https://" + workspace_url +"/serving-endpoints/" + agent
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
