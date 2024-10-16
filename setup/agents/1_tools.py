# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC # Functions/Tool Creation in Unity Catalog

# COMMAND ----------

# MAGIC %pip install PyYAML
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ../config

# COMMAND ----------

import os

host = "https://" + spark.conf.get("spark.databricks.workspaceUrl")

spark.sql(f"DROP FUNCTION IF EXISTS {catalog_name}.{schema_name}.fn_open_finance_faq")

spark.sql(f'''
CREATE OR REPLACE FUNCTION {catalog_name}.{schema_name}.fn_open_finance_faq (short_description STRING, databricks_token STRING)
RETURNS STRING
LANGUAGE PYTHON
COMMENT 'Returns information based on questions about open finance'
AS
$$
  try:
    import requests
    headers = {{"Authorization": "Bearer "+databricks_token}}

    response = requests.post("{host}/api/2.0/vector-search/indexes/{catalog_name}.{schema_name}.vs_open_finance_faq/query", json ={{"columns":"Comments","query_text":short_description, "num_results":1}}, headers=headers).json().get('result', {{}}).get('data_array', [])

    description, similarity_score = zip(*[(item[0], float(item[1])) for item in response])
    return description

  except Exception as e:
    return f"Error calling the vs index {{e}}"
$$;''')

# COMMAND ----------

spark.sql(f"DROP FUNCTION IF EXISTS {catalog_name}.{schema_name}.fn_send_email")

spark.sql(f'''
CREATE FUNCTION {catalog_name}.{schema_name}.fn_send_email (content STRING)
RETURNS STRING
LANGUAGE PYTHON
COMMENT 'Send email with content'
AS
$$
  try:
    return "Email sent successfully"
  except Exception as e:
    return f"Error sending email {{e}}"
$$;''')