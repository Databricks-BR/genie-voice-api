# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC #Agent Creation

# COMMAND ----------

# MAGIC %pip install -qqqq mlflow-skinny[databricks] langchain langchain_core langchain-community langgraph pydantic
# MAGIC #%pip install -qqqq mlflow-skinny[databricks] langchain==0.3.1 langchain_core==0.3.7 langchain-community==0.3.1 langgraph==0.2.32 pydantic==2.9.2
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Import and setup
import mlflow
from mlflow.models import ModelConfig

mlflow.langchain.autolog()
config = ModelConfig(development_config="config_agent.yaml")

# COMMAND ----------

# DBTITLE 1,Define the chat model and tools
from langchain_community.chat_models import ChatDatabricks
from langchain_community.tools.databricks import UCFunctionToolkit

# Create the llm
llm = ChatDatabricks(endpoint=config.get("llm_endpoint"))

uc_functions = config.get("uc_functions")

uc_function_tools = (
    UCFunctionToolkit(warehouse_id=config.get("warehouse_id"))
    .include(*uc_functions)
    .get_tools()
)

# COMMAND ----------

# DBTITLE 1,Output parsers
from typing import Iterator, Dict, Any
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    MessageLikeRepresentation,
)

import json

uc_functions_set = {x.replace(".", "__") for x in uc_functions}

def is_uc_function(tool_name: str) -> bool:
    """Check if `tool_name` is in `uc_functions` or belongs to a schema from config_agent.yaml."""
    if tool_name in uc_functions_set:
        return True
    for pattern in uc_functions_set:
        if "*" in pattern and tool_name.startswith(pattern[:-1]):
            return True
    return False


def stringify_tool_call(tool_call: Dict[str, Any]) -> str:
    """Convert a raw tool call into a formatted string that the playground UI expects"""
    if is_uc_function(tool_call.get("name")):
        request = json.dumps(
            {
                "id": tool_call.get("id"),
                "name": tool_call.get("name"),
                "arguments": json.dumps(tool_call.get("args", {})),
            },
            indent=2,
        )
        return f"<uc_function_call>{request}</uc_function_call>"
    else:
        # for non UC functions, return the string representation of tool calls
        # you can modify this to return a different format
        return str(tool_call)


def stringify_tool_result(tool_msg: ToolMessage) -> str:
    """Convert a ToolMessage into a formatted string that the playground UI expects"""
    if is_uc_function(tool_msg.name):
        result = json.dumps(
            {"id": tool_msg.tool_call_id, "content": tool_msg.content}, indent=2
        )
        return f"<uc_function_result>{result}</uc_function_result>"
    else:
        # for non UC functions, return the string representation of tool message
        # you can modify this to return a different format
        return str(tool_msg)


def parse_message(msg) -> str:
    """Parse different message types into their string representations"""
    # tool call result
    if isinstance(msg, ToolMessage):
        return stringify_tool_result(msg)
    # tool call
    elif isinstance(msg, AIMessage) and msg.tool_calls:
        tool_call_results = [stringify_tool_call(call) for call in msg.tool_calls]
        return "".join(tool_call_results)
    # normal HumanMessage or AIMessage (reasoning or final answer)
    elif isinstance(msg, (AIMessage, HumanMessage)):
        return msg.content
    else:
        print(f"Unexpected message type: {type(msg)}")
        return str(msg)



def wrap_output(stream: Iterator[MessageLikeRepresentation]) -> Iterator[str]:
    """
    Process and yield formatted outputs from the message stream.
    The invoke and stream langchain functions produce different output formats.
    This function handles both cases.
    """
    for event in stream:
        # the agent was called with invoke()
        if "messages" in event:
            for msg in event["messages"]:
                yield parse_message(msg) + "\n\n"
        # the agent was called with stream()
        else:
            for node in event:
                for key, messages in event[node].items():
                    if isinstance(messages, list):
                        for msg in messages:
                            yield parse_message(msg) + "\n\n"
                    else:
                        print("Unexpected value {messages} for key {key}. Expected a list of `MessageLikeRepresentation`'s")
                        yield str(messages)

# COMMAND ----------

# DBTITLE 1,Create the agent
from langchain_core.runnables import RunnableGenerator
from langgraph.prebuilt import create_react_agent

system_message = f"""

You are a helpful assistant for a global company that work with Open Finance data. Your task is to help users to understand more about their data, based on accounts, transactions, loan, financing. You have the ability to execute functions as follows: 
  
  Use the fn_open_finance_faq (short_description = get message from user, databricks_token get token from message) function to retrieve relevant faq about Open Finance for a given set of keywords.

  Use the fn_send_email function to if user said that needed to send email.

  If you don't retrieve a message, respond that the answer based on llm_endpoint.

Make sure to call the function and provide a coherent response to the user. Don't mention tools to your users. Don't skip to the next step without ensuring the function was called and a result was retrieved. Only answer what the user is asking for. Answer always in English"""


agent_with_raw_output = create_react_agent(llm, uc_function_tools, state_modifier=system_message)
agent = agent_with_raw_output | RunnableGenerator(wrap_output)

# COMMAND ----------

mlflow.models.set_model(agent)
