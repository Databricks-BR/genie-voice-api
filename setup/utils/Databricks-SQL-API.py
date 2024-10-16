# Databricks notebook source
import requests
import dbruntime

class DatabricksSQLAPI:
  def __init__(self, API_KEY):
    self.__url = "https://" + spark.conf.get("spark.databricks.workspaceUrl") + "/api/2.0"
    self.__api_key = API_KEY
    self.__headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": f"Bearer {self.__api_key}",
    }

  def __make_request(self, method, query, **kwargs):
    response = requests.request(
      method, f"{self.__url}{query}", headers=self.__headers, **kwargs
    )
    response.raise_for_status()
    return response

  def list_serverless_warehouses(self):
    response = self.__make_request("get", f"/sql/warehouses").json()["warehouses"]
    warehouses = []
    for warehouse in response:
      if warehouse["enable_serverless_compute"]:
        warehouses.append(
          {
            "id": warehouse["id"],
            "name": warehouse["name"],
          }
        )
    return warehouses

  def get_warehouse_by_name(self, warehouse_name: str):
    warehouses = self.list_serverless_warehouses()
    for warehouse in warehouses:
      if warehouse["name"] == warehouse_name:
        return warehouse
    return None

  def get_warehouse_id(self, warehouse_name: str):
    return self.get_warehouse_by_name(warehouse_name)["id"]