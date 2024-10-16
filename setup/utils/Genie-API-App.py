# Databricks notebook source
# MAGIC %pip install --quiet -U mlflow databricks-sdk==0.23.0
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./utils/lakehouse-app-helper

# COMMAND ----------

# MAGIC %%writefile ./lha/main.py
# MAGIC
# MAGIC import gradio as gr
# MAGIC import requests
# MAGIC import time
# MAGIC import json
# MAGIC import pandas as pd
# MAGIC from tabulate import tabulate
# MAGIC
# MAGIC
# MAGIC
# MAGIC # Configurações da API
# MAGIC HOST = "https://" + spark.conf.get("spark.databricks.workspaceUrl")  # Substitua pelo URL da sua instância do Databricks
# MAGIC #TOKEN = "dapi.......................f47t9b120"  # Substitua pelo seu token do Databricks
# MAGIC TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
# MAGIC API_PREFIX = "/api/2.0/genie/spaces"  # Prefixo da API
# MAGIC conversation_id = None 
# MAGIC conversation_started = False
# MAGIC SPACE_ID = "01xxxxxxxxxxxxxxxxxxxxxx7d819a3b"  # Substitua pelo ID do espaço
# MAGIC HEADERS = {'Authorization': 'Bearer {}'.format(TOKEN)}
# MAGIC
# MAGIC
# MAGIC # Função para enviar uma mensagem para o Genie
# MAGIC # Funções para comunicação com a API Genie
# MAGIC def post(endpoint, data):
# MAGIC     resp = requests.post(
# MAGIC         HOST + endpoint,
# MAGIC         json=data,
# MAGIC         headers=HEADERS
# MAGIC     )
# MAGIC
# MAGIC     print("URL:", resp.request.url)
# MAGIC     print("Body:", resp.request.body)
# MAGIC     print("Headers:", resp.request.headers)
# MAGIC
# MAGIC     resp.raise_for_status()
# MAGIC     return resp.json()
# MAGIC
# MAGIC def get(endpoint):
# MAGIC     resp = requests.get(
# MAGIC         HOST + endpoint,
# MAGIC         headers=HEADERS
# MAGIC     )
# MAGIC     resp.raise_for_status()
# MAGIC     return resp.json()
# MAGIC
# MAGIC def start_conversation(content):
# MAGIC   resp = post(
# MAGIC     f"/api/2.0/genie/spaces/{SPACE_ID}/start-conversation", 
# MAGIC     {
# MAGIC       "content": content,
# MAGIC     }
# MAGIC   )
# MAGIC   return resp
# MAGIC
# MAGIC def create_message(conversation_id, content):
# MAGIC   resp = post(
# MAGIC     f"/api/2.0/genie/spaces/{SPACE_ID}/conversations/{conversation_id}/messages",
# MAGIC     {
# MAGIC       "content": content
# MAGIC     }
# MAGIC   )
# MAGIC   return resp
# MAGIC
# MAGIC def poll_for_result(conversation_id, message_id):
# MAGIC     def poll_result():
# MAGIC         while True:
# MAGIC             resp = get(f"/api/2.0/genie/spaces/{SPACE_ID}/conversations/{conversation_id}/messages/{message_id}")
# MAGIC             if resp['status'] == "EXECUTING_QUERY":
# MAGIC                 sql = next(r for r in resp['attachments'] if 'query' in r)['query']['query']
# MAGIC                 print(f"SQL: {sql}")
# MAGIC                 return poll_query_results()
# MAGIC             elif resp['status'] == 'COMPLETED':
# MAGIC                 return next(r for r in resp['attachments'] if 'text' in r)['text']['content']
# MAGIC             else:
# MAGIC                 print(f"Waiting...: {resp['status']}")
# MAGIC                 time.sleep(5)
# MAGIC
# MAGIC     def poll_query_results():
# MAGIC         while True:
# MAGIC             resp = get(f"/api/2.0/genie/spaces/{SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/query-result")['statement_response']
# MAGIC             state = resp['status']['state']
# MAGIC             if state == 'SUCCEEDED':
# MAGIC                 data = resp['result']
# MAGIC                 meta = resp['manifest']
# MAGIC                 rows = [[c['str'] for c in r['values']] for r in data['data_typed_array']]
# MAGIC                 columns = [c['name'] for c in meta['schema']['columns']]
# MAGIC                 #df = spark.createDataFrame(rows, schema=columns)
# MAGIC                 df = pd.DataFrame(rows, columns=columns)
# MAGIC                 #print(df)
# MAGIC             # Verifica o número de colunas e formata o resultado
# MAGIC                 if len(df.columns) > 1:
# MAGIC                     # Formata e exibe o Pandas DataFrame como uma tabela
# MAGIC                     df_html = tabulate(df, headers='keys', tablefmt='html')
# MAGIC                     df_html = f"""
# MAGIC                     <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);">
# MAGIC                         {df_html}
# MAGIC                     </div>
# MAGIC                     """
# MAGIC                     return df_html
# MAGIC                 else:
# MAGIC                     # Exibe o Pandas DataFrame sem formatação tabular
# MAGIC                     text = df.to_string(index=False)
# MAGIC                     text_with_extra_breaks = text.replace('\n', '<br><br>')
# MAGIC                     escaped_text = html.escape(text_with_extra_breaks)
# MAGIC                     df_html = f"""
# MAGIC                     <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);">
# MAGIC                         <pre>{escaped_text}</pre>
# MAGIC                     </div>
# MAGIC                     """
# MAGIC                     return df_html
# MAGIC             elif state == 'RUNNING' or state == 'PENDING':
# MAGIC                 print(f"Waiting for query result...")
# MAGIC                 time.sleep(5)
# MAGIC             else:
# MAGIC                 print(f"No query result: {resp['state']}")
# MAGIC                 return None
# MAGIC
# MAGIC     return poll_result()
# MAGIC
# MAGIC
# MAGIC def send_message_to_genie(message):
# MAGIC     global conversation_started, conversation_id
# MAGIC     
# MAGIC     if not conversation_started:
# MAGIC         # Primeira interação: inicia a conversa
# MAGIC         start_resp = start_conversation(message)
# MAGIC         conversation_id = start_resp['conversation_id']
# MAGIC         message_id = start_resp['message_id']
# MAGIC         
# MAGIC         print("Conversation started:")
# MAGIC         print("Conversation ID:", conversation_id)
# MAGIC         print("Message ID:", message_id)
# MAGIC
# MAGIC         print("Create message response:", start_resp)
# MAGIC         
# MAGIC         # Define que a conversa foi iniciada
# MAGIC         conversation_started = True
# MAGIC
# MAGIC         # Poll para o resultado após iniciar a conversa
# MAGIC         result = poll_for_result(conversation_id, message_id)
# MAGIC         return result
# MAGIC     else:
# MAGIC         # Segunda interação e subsequentes: cria mensagem
# MAGIC         print("Conversation already started. Sending new message.")
# MAGIC
# MAGIC         create_message_resp = create_message(conversation_id, message)
# MAGIC         conversation_id = create_message_resp['conversation_id']
# MAGIC         message_id = create_message_resp['id']
# MAGIC
# MAGIC         #print("Create message response:", create_message_resp)
# MAGIC         #return create_message_resp
# MAGIC
# MAGIC         result = poll_for_result(conversation_id, message_id)
# MAGIC         return result
# MAGIC     
# MAGIC     # Poll para o resultado (opcional, depende de como funciona no seu fluxo)
# MAGIC     #result = poll_for_result(conversation_id, message_id)
# MAGIC     #return result
# MAGIC
# MAGIC
# MAGIC #TODO Corrigir trecho abaixo para definir url de forma automatizada
# MAGIC # HTML para o iframe
# MAGIC iframe_html = """
# MAGIC <iframe src="https://e2-demo-field-eng.cloud.databricks.com/embed/dashboardsv3/01ef4a7d20ad1fd5a903273b19d24aea?o=1444828305810485" width="100%" height="600" frameborder="0"></iframe>
# MAGIC """
# MAGIC
# MAGIC # Cria a interface do Gradio
# MAGIC iface = gr.Blocks()
# MAGIC
# MAGIC with iface:
# MAGIC     with gr.Row():
# MAGIC         # Adiciona o componente de chatbot na primeira coluna
# MAGIC         with gr.Column(scale=1):
# MAGIC             gr.Markdown("## Chatbot Genie")
# MAGIC             chatbot_input = gr.Textbox(label="Digite sua mensagem:", placeholder="Digite aqui...")
# MAGIC             #chatbot_output = gr.Textbox(label="Resposta do Genie:", interactive=False, placeholder="A resposta aparecerá aqui...")
# MAGIC             chatbot_output = gr.HTML(label="Resposta do Genie:")  # Mantém gr.HTML para exibir o resultado formatado
# MAGIC             chatbot_btn = gr.Button("Enviar")
# MAGIC             chatbot_btn.click(fn=send_message_to_genie, inputs=chatbot_input, outputs=chatbot_output)
# MAGIC         
# MAGIC         # Adiciona o componente HTML para o iframe na segunda coluna
# MAGIC         with gr.Column(scale=2):
# MAGIC             gr.HTML(iframe_html)
# MAGIC
# MAGIC # Lança o aplicativo
# MAGIC iface.launch(share=True)

# COMMAND ----------

app_name = "genie-api-demo-app"

#Helper is defined in the _resources/02-lakehouse-app-helpers notebook (temporary helper)
helper = LakehouseAppHelper()
app_details = helper.create(app_name, app_description="Your Databricks assistant")

# COMMAND ----------

import os
helper.deploy(app_name, os.path.join(os.getcwd(), 'lha'))
helper.details(app_name)
