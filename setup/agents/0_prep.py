# Databricks notebook source
# MAGIC %run ../config

# COMMAND ----------

# MAGIC %run ../utils/Databricks-SQL-API

# COMMAND ----------

import yaml
import os

token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

databricksSqlAPI = DatabricksSQLAPI(token)
warehouse_id = databricksSqlAPI.get_warehouse_id(warehouse_name=warehouse_name)

config_agent = {
  "llm_endpoint": f"{llm_endpoint}",
  "warehouse_id": f"{warehouse_id}",
  "uc_functions": [f"{catalog_name}.{schema_name}.fn_open_finance_faq",f"{catalog_name}.{schema_name}.fn_send_email"]
}

config_data = {
    "catalog_name": f"{catalog_name}",
    "schema_name": f"{schema_name}",
    "agent_name": f"{agent_name}"
}

with open("config_data.yaml", "w") as file:
    yaml.dump(config_data, file)

with open("config_agent.yaml", "w") as file:
    yaml.dump(config_agent, file)



# COMMAND ----------

