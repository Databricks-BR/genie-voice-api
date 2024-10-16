import requests
import json
import pandas as pd
import time
from tabulate import tabulate
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

workspace_client = WorkspaceClient()

class GenieAPI:

    def __init__(self, token, workspace_url, space_id):
        self.__token = token
        self.space_id = space_id
        self.__base_url = "https://" + workspace_url +f"/api/2.0/genie/spaces/{self.space_id}"
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
            
            print(resp)

            state = resp['status']['state']
            
            if state == 'SUCCEEDED':
                data = resp['result']
                if not data:
                    return "No data available - Check check at Genie Space"
                meta = resp['manifest']
                # TODO check if row [value] is empty
                rows = [[c['str'] for c in r['values']] for r in data['data_typed_array']]
                columns = [c['name'] for c in meta['schema']['columns']]
                df = pd.DataFrame(rows, columns=columns)

                if len(df.columns) > 1:
                    df = tabulate(df, headers='keys', tablefmt='html')
                    return df
                else:
                    text = df.to_string(index=False)
                    return text

            elif state == 'RUNNING' or state == 'PENDING':
                time.sleep(5)            
            else:
                return None
                  
    def poll_for_result(self, conversation_id, message_id):
        while True:
            resp = requests.get(f"{self.__base_url}/conversations/{conversation_id}/messages/{message_id}", headers=self.__headers)
            resp.raise_for_status()
            resp = resp.json()
            if resp['status'] == "EXECUTING_QUERY":
                sql = next((r for r in resp['attachments'] if 'query' in r), {}).get('query', {}).get('content', 'Result not found sql')
                if sql:
                    return self.poll_query_results(conversation_id, message_id)
                return None
            elif resp['status'] in ('SUBMITTED', 'FILTERING_CONTEXT', 'ASKING_AI'):
                time.sleep(5)
            elif resp['status'] == 'COMPLETED':
                return next((r for r in resp['attachments'] if 'text' in r), {}).get('text', {}).get('content', 'Result not found')
            else:
                time.sleep(5)
      
    def send_message_to_genie(self, conversation_id, message):
        if conversation_id == "0":            
            start_resp = self.start_conversation(message)
            conversation_id = start_resp['conversation_id']
            message_id = start_resp['message_id']
        elif not conversation_id.isdigit():
            start_resp = self.start_conversation(message)
            conversation_id = start_resp['conversation_id']
            message_id = start_resp['message_id']
        else:
            create_message_resp = self.create_message(conversation_id, message)                        
            conversation_id = create_message_resp['conversation_id']
            message_id = create_message_resp['id']
        
        result = self.poll_for_result(conversation_id, message_id)

        if result:
            result_formatted = self.query_model_format(result)
        else:
            result_formatted = "Result not found in Genie"

        return conversation_id, result_formatted
        
    def query_model_format(self, text_to_format):
        w = WorkspaceClient()
       
        prompt = "answer using bullets and sub-bullets. Format the message in a clear and organized way. Short answer. Do not need to show the prompt information as \"Here is a summary of the data in a clear and organized way\". Do not show SQL instructions to user. Answer always using the same language as the prompt."

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
