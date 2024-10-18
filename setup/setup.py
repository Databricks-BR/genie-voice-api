# Databricks notebook source
# DBTITLE 1,Data Gen
# MAGIC %md
# MAGIC # SETUP
# MAGIC
# MAGIC ## Requirements:
# MAGIC Set your catalog and schema name at config file

# COMMAND ----------

!pip install --upgrade -qqq databricks-sdk
!pip install databricks-vectorsearch

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./config

# COMMAND ----------

if not spark.sql(f"SHOW CATALOGS LIKE '{catalog_name}'").collect():
  spark.sql(f"CREATE CATALOG {catalog_name}")

if not spark.sql(f"SHOW SCHEMAS IN {catalog_name} LIKE '{schema_name}'").collect():
  spark.sql(f"CREATE SCHEMA {catalog_name}.{schema_name}")

# COMMAND ----------

# MAGIC %run ./datagen/00_open_finance_data_generator

# COMMAND ----------

# Get random personal_id to be used at instructions for Genie Space
personal_id = spark.sql(f"select personal_id FROM {catalog_name}.{schema_name}.tb_transaction limit 1").collect()[0]['personal_id']
instructions = f"""- Expenses, costs, payments: use the operation column that contains DEBIT
- r2d2 or r2-d2: use the personal_id field = '{personal_id}'
-'Income', 'Salary', 'Bonus', 'Reimbursement', 'Benefits': use the operation column that contains CREDIT
- for payment methods use the type column and operation = DEBIT
- future entries: consider transaction date greater than today and operation = DEBIT
- financial planning: DEBIT and CREDIT operations with transaction date greater than today
- planning assistance: select the 5 largest DEBIT operations"""

# COMMAND ----------

# MAGIC %md 
# MAGIC # Creating FAQ table for Vector Search

# COMMAND ----------

spark.sql(f"CREATE VOLUME IF NOT EXISTS {catalog_name}.{schema_name}.datasets")
spark.sql(f"DROP TABLE IF EXISTS {catalog_name}.{schema_name}.tb_faq")

# COMMAND ----------

import shutil

src_path = "./datagen/open_banking_faq.csv"
dst_path = f"/Volumes/{catalog_name}/{schema_name}/datasets/open_banking_faq.csv"

try:
  shutil.copy(src_path, dst_path)
except Exception as e:
  print(e)

# COMMAND ----------

from pyspark.sql.functions import monotonically_increasing_id

df = spark.read.option("multiline", "true").csv(f"/Volumes/{catalog_name}/{schema_name}/datasets/open_banking_faq.csv", header=True, sep=";")

df = df.withColumn("id", monotonically_increasing_id())

df.write.format("delta").mode("append").saveAsTable(f"{catalog_name}.{schema_name}.tb_faq")

# COMMAND ----------

spark.sql(f"ALTER TABLE {catalog_name}.{schema_name}.tb_faq SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

# COMMAND ----------

# MAGIC %md 
# MAGIC # Deploy Whisper Model

# COMMAND ----------

version = "2"
model_name = "whisper_large_v3"
model_uc_path = "system.ai.whisper_large_v3"
whisper_endpoint_name = f'{model_name}_endpoint'

workload_type = "GPU_SMALL"

# COMMAND ----------

# DBTITLE 1,Deploy Whisper (ETA: 1 hour)
import datetime

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput
w = WorkspaceClient()

config = EndpointCoreConfigInput.from_dict({
    "served_models": [
        {
            "name": whisper_endpoint_name,
            "model_name": model_uc_path,
            "model_version": version,
            "workload_type": workload_type,
            "workload_size": "Small",
            "scale_to_zero_enabled": "True",
        }
    ]
})

try:
    print("Submitting Whisper Deploy - Estimated Time: 1 hour")
    model_details = w.serving_endpoints.create(name=whisper_endpoint_name, config=config)
    model_details.result(timeout=datetime.timedelta(minutes=60)) 
except:
    print("Whisper already exists - Not Redeployed")

# COMMAND ----------

# MAGIC %md
# MAGIC # Deploy Dashboard

# COMMAND ----------

dashboard_spec = {"datasets":[{"displayName":"tb_accounts","name":"23fa4612","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_accounts"},{"displayName":"tb_bank","name":"18c3fe46","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_bank"},{"displayName":"tb_financing","name":"2ee62e4a","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_financing"},{"displayName":"tb_loan","name":"6efa49fd","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_loan"},{"displayName":"tb_personal","name":"c7666f6b","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_personal"},{"displayName":"tb_transaction","name":"4516e654","query":f"SELECT * FROM {catalog_name}.{schema_name}.tb_transaction"}],"pages":[{"displayName":"New Page","layout":[{"position":{"height":5,"width":2,"x":2,"y":0},"widget":{"name":"70c867fc","queries":[{"name":"main_query","query":{"datasetName":"4516e654","disaggregated":False,"fields":[{"expression":"SUM(`value`)","name":"sum(value)"},{"expression":"`type`","name":"type"}]}}],"spec":{"encodings":{"label":{"show":True},"x":{"displayName":"Amount ($)","fieldName":"sum(value)","scale":{"type":"quantitative"}},"y":{"displayName":"Type","fieldName":"type","scale":{"sort":{"by":"x-reversed"},"type":"categorical"}}},"frame":{"showDescription":False,"showTitle":True,"title":"Transactions"},"version":3,"widgetType":"bar"}}},{"position":{"height":5,"width":2,"x":4,"y":0},"widget":{"name":"8fe51c6d","queries":[{"name":"main_query","query":{"datasetName":"4516e654","disaggregated":False,"fields":[{"expression":"`type`","name":"type"},{"expression":"`data_transaction`","name":"data_transaction"},{"expression":"SUM(`value`)","name":"sum(value)"}]}}],"spec":{"encodings":{"color":{"displayName":"Type","fieldName":"type","scale":{"type":"categorical"}},"x":{"displayName":"Data da Transacao","fieldName":"data_transaction","scale":{"type":"categorical"}},"y":{"displayName":"Amount ($)","fieldName":"sum(value)","scale":{"type":"quantitative"}}},"frame":{"showTitle":True,"title":"Income vs Expenses per Year"},"version":3,"widgetType":"bar"}}},{"position":{"height":8,"width":6,"x":0,"y":11},"widget":{"name":"1378e297","queries":[{"name":"main_query","query":{"datasetName":"4516e654","disaggregated":False,"fields":[{"expression":"`category`","name":"category"},{"expression":"`data_transaction`","name":"data_transaction"},{"expression":"SUM(`value`)","name":"sum(value)"}]}}],"spec":{"encodings":{"color":{"displayName":"category","fieldName":"category","scale":{"type":"categorical"}},"x":{"displayName":"data_transaction","fieldName":"data_transaction","scale":{"type":"categorical"}},"y":{"displayName":"Sum of value","fieldName":"sum(value)","scale":{"type":"quantitative"}}},"frame":{"showTitle":True,"title":"Total expenses by category over time"},"version":3,"widgetType":"bar"}}},{"position":{"height":5,"width":2,"x":0,"y":0},"widget":{"name":"cf6ca91d","queries":[{"name":"main_query","query":{"datasetName":"4516e654","disaggregated":False,"fields":[{"expression":"SUM(`value`)","name":"sum(value)"}]}}],"spec":{"encodings":{"value":{"displayName":"Sum of value","fieldName":"sum(value)"}},"frame":{"showTitle":True,"title":"Annual income"},"version":2,"widgetType":"counter"}}},{"position":{"height":6,"width":6,"x":0,"y":5},"widget":{"name":"a1b86ca9","queries":[{"name":"main_query","query":{"datasetName":"4516e654","disaggregated":False,"fields":[{"expression":"`operation`","name":"operation"},{"expression":"DATE_TRUNC(\"DAY\", `data_transaction`)","name":"daily(data_transaction)"},{"expression":"SUM(`value`)","name":"sum(value)"}]}}],"spec":{"encodings":{"color":{"displayName":"Operation","fieldName":"operation","scale":{"type":"categorical"}},"x":{"displayName":"data_transaction","fieldName":"daily(data_transaction)","scale":{"type":"temporal"}},"y":{"displayName":"Amount ($)","fieldName":"sum(value)","scale":{"type":"quantitative"}}},"frame":{"showTitle":True,"title":"Debits and Credits per Day"},"version":3,"widgetType":"line"}}}],"name":"f11cbca6"}]}

# COMMAND ----------

# MAGIC %run ./utils/Databricks-Dashboard-API

# COMMAND ----------

import dbruntime

DASHBOARD_TEMPLATE = dashboard_spec
CURRENT_USER = spark.sql("SELECT current_user() AS user").collect()[0]['user']
WORKSPACE_DASHBOARDS_FOLDER = os.path.dirname(os.getcwd()) #"/Workspace/Users/"+CURRENT_USER
DASHBOARD_NAME='OPEN_FINANCE_DEMO'

# Get the token from the current notebook context
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

databricks = DashboardUtil(token)

# COMMAND ----------

new_dashboard = databricks.create_and_publish_dashboard(dashboard_folder=WORKSPACE_DASHBOARDS_FOLDER,dashboard_spec=DASHBOARD_TEMPLATE, warehouse_name=warehouse_name,dashboard_name=DASHBOARD_NAME)
dashboard_resource_id = new_dashboard.get("resource_id")

#dashboard_resource_id = databricks.get_dashboard_resource_id(dashboard_folder=WORKSPACE_DASHBOARDS_FOLDER,dashboard_name=DASHBOARD_NAME)


# COMMAND ----------

workspace_url = dbruntime.databricks_repl_context.get_context().browserHostName
workspace_id = dbruntime.databricks_repl_context.get_context().workspaceId

dash_url = "https://" + workspace_url + "/embed/dashboardsv3/" + dashboard_resource_id + "?o=" + workspace_id

dash_url

# COMMAND ----------

# MAGIC %md
# MAGIC # Prep APP

# COMMAND ----------

import os
import glob

# Define the directory containing the files
directory_path = os.path.dirname(os.getcwd()) + "/app/static/static/js/"

# Get all filenames that start with 'main' and end with '.js'
file_paths = glob.glob(os.path.join(directory_path, "main.*.js*"))
print("files to update: " + str(file_paths))
# Loop through each file and apply the replace operation
for file_path in file_paths:
    # Read the content of the file
    with open(file_path, 'r') as file:
        print("updating file: " + file_path)
        file_content = file.read()

    import re
    new_file_content = re.sub(r"https:\/\/[0-9,a-z,\-]{3,24}(\.cloud)?\.(azure)?databricks\.(com|net)\/embed\/dashboardsv3\/[0-9|a-z]{32}\?o=[0-9]{16}", dash_url, file_content)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(new_file_content)

# COMMAND ----------

# MAGIC %md
# MAGIC # Deploy Vector Search

# COMMAND ----------

import time

def endpoint_exists(vsc,endpoint_name):
  try:
    vsc.get_endpoint(endpoint_name)
    return True
  except Exception as e:
    print(f'Vector Search Endpoint Name "{endpoint_name}" does not exist')
    return False

def index_exists(vsc, endpoint_name, index_full_name):
    try:
        vsc.get_index(endpoint_name, index_full_name).describe()
        return True
    except Exception as e:
        if 'RESOURCE_DOES_NOT_EXIST' not in str(e):
            print(f'Unexpected error describing the index. This could be a permission issue.')
            raise e
    return False
    
def wait_for_index_to_be_ready(vsc, vs_endpoint_name, index_name):
  for i in range(180):
    idx = vsc.get_index(vs_endpoint_name, index_name).describe()
    index_status = idx.get('status', idx.get('index_status', {}))
    status = index_status.get('detailed_state', index_status.get('status', 'UNKNOWN')).upper()
    url = index_status.get('index_url', index_status.get('url', 'UNKNOWN'))
    if "ONLINE" in status:
      return
    if "UNKNOWN" in status:
      print(f"Can't get the status - will assume index is ready {idx} - url: {url}")
      return
    elif "PROVISIONING" in status:
      if i % 40 == 0: print(f"Waiting for index to be ready, this can take a few min... {index_status} - pipeline url:{url}")
      time.sleep(10)
    else:
        raise Exception(f'''Error with the index - this shouldn't happen. DLT pipeline might have been killed.\n Please delete it and re-run the previous cell: vsc.delete_index("{index_name}, {vs_endpoint_name}") \nIndex details: {idx}''')
  raise Exception(f"Timeout, your index isn't ready yet: {vsc.get_index(index_name, vs_endpoint_name)}")

def wait_for_model_serving_endpoint_to_be_ready(ep_name):
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.serving import EndpointStateReady, EndpointStateConfigUpdate
    import time

    # Wait for it to be ready
    w = WorkspaceClient()
    state = ""
    for i in range(200):
        state = w.serving_endpoints.get(ep_name).state
        if state.config_update == EndpointStateConfigUpdate.IN_PROGRESS:
            if i % 40 == 0:
                print(f"Waiting for endpoint to deploy {ep_name}. Current state: {state}")
            time.sleep(10)
        elif state.ready == EndpointStateReady.READY:
          print('endpoint ready.')
          return
        else:
          break
    raise Exception(f"Couldn't start the endpoint, timeout, please check your endpoint for more details: {state}")

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient
from databricks.sdk import WorkspaceClient
import databricks.sdk.service.catalog as c
import json

vsc = VectorSearchClient()

source_table_fullname = f"{catalog_name}.{schema_name}.tb_faq"
vs_index_fullname = f"{catalog_name}.{schema_name}.vs_open_finance_faq"

if endpoint_exists(vsc, vs_endpoint_name):
  if not index_exists(vsc, vs_endpoint_name, vs_index_fullname):
    print(f"Creating index {vs_index_fullname} on endpoint {vs_endpoint_name}...")

    try:
      vsc.create_delta_sync_index(
        endpoint_name=vs_endpoint_name,
        index_name=vs_index_fullname,
        source_table_name=source_table_fullname,
        pipeline_type="TRIGGERED",
        primary_key="id",
        embedding_source_column="Comments",
        embedding_model_endpoint_name="databricks-bge-large-en"
      )
      wait_for_index_to_be_ready(vsc, vs_endpoint_name, vs_index_fullname)
    except Exception as e:
      if 'QUOTA_EXCEEDED' in str(e):
        print(f"Error: Quota exceeded while creating index {vs_index_fullname} on endpoint {vs_endpoint_name}.")
        print(f"Select another! Available Endpoints:")
        aux = [endpoint['name'] for endpoint in vsc.list_endpoints()['endpoints'] if endpoint.get('num_indexes', 0) < 50]
        print(aux)
        print("--")
        raise Exception(
          f"Error: Quota exceeded while creating index {vs_index_fullname} on endpoint {vs_endpoint_name}.\nSelect another endpoint and update the config file and run setup again.")
      else:
        raise e
  else:
    vsc.get_index(vs_endpoint_name, vs_index_fullname).sync()
else:
  raise Exception(f"Vector Search Endpoint Name {vs_endpoint_name} does not exist")

# COMMAND ----------

# MAGIC %md
# MAGIC # Deploy Agents

# COMMAND ----------

# MAGIC %run ./agents/0_prep

# COMMAND ----------

# MAGIC %run ./agents/1_tools

# COMMAND ----------

# MAGIC %run ./agents/2_agent

# COMMAND ----------

# MAGIC %run ./agents/3_register

# COMMAND ----------

# MAGIC %md
# MAGIC # Prep Deploy Lakehouse APP

# COMMAND ----------

import os
import glob

# Define the directory containing the files
directory_path = os.path.dirname(os.getcwd()) + "/app/static/static/js/"

# Get all filenames that start with 'main' and end with '.js'
file_paths = glob.glob(os.path.join(directory_path, "main.*.js*"))
print("files to update: " + str(file_paths))
# Loop through each file and apply the replace operation
for file_path in file_paths:
    # Read the content of the file
    with open(file_path, 'r') as file:
        print("updating file: " + file_path)
        file_content = file.read()

    import re
    # Replace the old URL with the new one from app_details['url']
    new_file_content = re.sub(r"https:\/\/[0-9|a-z|-]{1,30}-[0-9]{16}\.(azure|aws)\.databricksapps\.com", app_details['url'], file_content)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(new_file_content)

# COMMAND ----------

file_path = os.path.dirname(os.getcwd())+"/app/app.py"
with open(file_path, 'r') as file:
    print("updating file: " + file_path)
    file_content = file.read()

import re
new_file_content = re.sub(r"(agent_api = AgentAPI\(token=token,workspace_url=os\.getenv\(\'DATABRICKS_HOST\'\),agent=\')([^']*)('.*)", r"\1" + agent_name + r"\3", file_content)

# Write the updated content back to the file
with open(file_path, 'w') as file:
    file.write(new_file_content)

# COMMAND ----------

# MAGIC %md
# MAGIC # Deploy Lakehouse APP

# COMMAND ----------

# MAGIC %run ./utils/lakehouse-app-helper

# COMMAND ----------

helper = LakehouseAppHelper()

# COMMAND ----------

# DBTITLE 1,Delete APP if exists
helper.delete(app_name)

# COMMAND ----------

# DBTITLE 1,Creating new Lakehouse APP
app_details = helper.create(app_name, app_description="Open Finance data analysis application")

# COMMAND ----------

helper.add_dependencies(
     app_name=app_name,
     dependencies=[
        {
          "name": "whisper-endpoint",
          "serving_endpoint": {
            "name": whisper_endpoint_name,
            "permission": "CAN_QUERY"
          }
        },
        {
          "name": "agent-endpoint",
          "serving_endpoint": {
            "name": agent_name,
            "permission": "CAN_QUERY"
          }
        }
     ],
     overwrite=True
 )

# COMMAND ----------

helper.deploy(app_name, os.path.dirname(os.getcwd())+"/app")
helper.details(app_name)

# COMMAND ----------

# MAGIC %md 
# MAGIC # CREATE GENIE SPACE AND TEST THE APP
# MAGIC Now that you already executed the setup you need to create the Genie Space (aka Data Room) for the generated data. 
# MAGIC
# MAGIC ## GENIE SPACE
# MAGIC 1. Access the Menu (Left Bar) `Genie`
# MAGIC 2. Click button `+ NEW`
# MAGIC 3. Create the Data Room
# MAGIC - Set the Title
# MAGIC - Select the Warehouse
# MAGIC - Add Tables and Confirm 
# MAGIC > Note: Use the **catalog** and **schema** mentioned at **config** file
# MAGIC      - `tb_accounts`
# MAGIC      - `tb_bank`
# MAGIC      - `tb_financing`
# MAGIC      - `tb_loan`
# MAGIC      - `tb_personal`
# MAGIC      - `tb_transaction`
# MAGIC - Click the button `Save`
# MAGIC - Copy the Instructions below to the Genie Space
# MAGIC
# MAGIC

# COMMAND ----------

print(instructions)

# COMMAND ----------

# MAGIC %md 
# MAGIC 4. Save the instructions 
# MAGIC 5. Copy the Genie Space ID at URL (it's the string after /genie/rooms/##SPACE_ID##?...)
# MAGIC
# MAGIC ## TEST APP
# MAGIC 1. Generate a new token (At top right click `Settings` -> `Developer` -> `Access Token` -> `Generate New Token`)
# MAGIC 2. Open the APP Link above and click at top right -> `Settings` and fill out the form
# MAGIC - Token (sample): `dapi..............15a48ecb546f9c56b7`
# MAGIC - Genie Space ID (sample): `01ef8a9c200f12eda257ff7caa320ff7`
# MAGIC - key words: "`r2d2,R2-D2`"
