# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC # Register Agent to UC
# MAGIC

# COMMAND ----------

# MAGIC %pip install -qqqq mlflow-skinny[databricks] langchain langchain_core langchain-community langgraph pydantic
# MAGIC #!pip install -qqqq databricks-agents mlflow[databricks] langchain==0.3.1 langchain_core==0.3.7 langchain-community==0.3.1 langgraph==0.2.34 pydantic==2.9.2
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ../config

# COMMAND ----------

# DBTITLE 1,Log the agent as an MLflow model
import os

input_example = {
    "messages": [
        {
            "role": "user",
            "content": "token=dapi..., message=What is Open Finance?"
        }
    ]
}

model_config_path = None
if os.path.exists(os.path.dirname(os.getcwd()) + "/setup/config_agent.yaml"):
    model_config_path= os.path.dirname(os.getcwd()) + "/setup/config_agent.yaml"
elif os.path.exists(os.path.dirname(os.getcwd()) + "/config_agent.yaml"):
    model_config_path= os.path.dirname(os.getcwd()) + "/config_agent.yaml"
else: 
    model_config_path = os.path.dirname(os.getcwd()) + "/agents/config_agent.yaml"  

print("model_config_path =",model_config_path)


log_model_path = None
if os.path.exists(os.path.dirname(os.getcwd()) + "/setup/agents/2_agent"):
    log_model_path= os.path.dirname(os.getcwd()) + "/setup/agents/2_agent"
elif os.path.exists(os.path.dirname(os.getcwd()) + "/agents/2_agent"):
    log_model_path= os.path.dirname(os.getcwd()) + "/agents/2_agent"
else: 
    log_model_path = os.path.dirname(os.getcwd()) + "/2_agent"

print("log_model =",log_model_path)

# COMMAND ----------

import mlflow

with mlflow.start_run():
    logged_agent_info = mlflow.langchain.log_model(
        lc_model=log_model_path,
        pip_requirements=[
             f"langchain==0.3.1",
             f"langchain-community==0.3.1",
             f"langchain_core==0.3.7",
             f"langgraph==0.2.34",
             f"pydantic==2.9.2",
        ],
        model_config=model_config_path,
        artifact_path='agent',
        input_example=input_example,
    )

# COMMAND ----------

# DBTITLE 1,Evaluate the agent with Agent Evaluation
import pandas as pd

eval_examples = [
    {
        "request": {
            "messages": [
                {
                    "role": "user",
                    "content": "token=dapi..., message=What is Open Finance?"
                }
            ]
        },
        "expected_response": None
    }
]

eval_dataset = pd.DataFrame(eval_examples)
display(eval_dataset)

# COMMAND ----------

import mlflow
import pandas as pd

with mlflow.start_run(run_id=logged_agent_info.run_id):
    eval_results = mlflow.evaluate(
        f"runs:/{logged_agent_info.run_id}/agent",
        data=eval_dataset,
        model_type="databricks-agent",
    )

# Review the evaluation results in the MLFLow UI (see console output), or access them in place:
display(eval_results.tables['eval_results'])

# COMMAND ----------

# DBTITLE 1,Register the model to Unity Catalog
import os
import yaml
from databricks.sdk import WorkspaceClient

# Grabs the username without the full email address. 
w = WorkspaceClient()

# config file created in 1_create_tools
with open("config_data.yaml", "r") as file:
    config_data = yaml.safe_load(file)

# Catalog and schema have been created in tools
catalog_name = config_data["catalog_name"]
schema_name = config_data["schema_name"]
agent_name = config_data["agent_name"]

# COMMAND ----------

catalog_name, schema_name, agent_name

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

UC_MODEL_NAME = f"{catalog_name}.{schema_name}.{agent_name}"

# register the model to UC
uc_registered_model_info = mlflow.register_model(model_uri=logged_agent_info.model_uri, name=UC_MODEL_NAME)

# COMMAND ----------

# DBTITLE 1,Deploy the agent
from databricks import agents

# Deploy the model to the review app and a model serving endpoint
try:
  print("Deploying model")
  agents.deploy(UC_MODEL_NAME, uc_registered_model_info.version, endpoint_name=f"{agent_name}", set_inference_table=False)
  print("Model deployed")
except Exception as e:
      if 'ResourceConflict' in str(e) and 'currently updating' in str(e):
        import time
        start_time = time.time()
        while time.time() - start_time < 300:
          print("Waiting for agent be ready to deploy...")
          try:
            status = agents.get_deploy_status(UC_MODEL_NAME, uc_registered_model_info.version)
            print(status)
            if status != 'currently updating':
              agents.deploy(UC_MODEL_NAME, uc_registered_model_info.version, endpoint_name=f"{agent_name}", set_inference_table=False)
              break
          except Exception as e:
            if 'ResourceConflict' in str(e) and 'currently updating' in str(e):
              continue
      else:
        raise e



# COMMAND ----------

if os.path.exists(model_config_path):
    os.remove(model_config_path)

if os.path.exists("config_data.yaml"):
    os.remove("config_data.yaml")
