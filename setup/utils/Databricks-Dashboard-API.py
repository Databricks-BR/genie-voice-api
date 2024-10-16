# Databricks notebook source
import base64
import json
import os
import requests
import dbruntime

class DashboardUtil:
    def __init__(self, API_KEY):
        self.url = "https://" + dbruntime.databricks_repl_context.get_context().browserHostName + "/api/2.0"
        self.api_key = API_KEY
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def make_request(self, method, query, **kwargs):
        response = requests.request(
            method, f"{self.url}{query}", headers=self.headers, **kwargs
        )
        response.raise_for_status()
        return response

    def list_serverless_warehouses(self):
        response = self.make_request("get", f"/sql/warehouses").json()["warehouses"]
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

    def create_dashboard(self, dashboard_spec: str,dashboard_folder: str,dashboard_name: str):
        request_data = {
            "path": f"{dashboard_folder}/{dashboard_name}.lvdash.json",
            "content": base64.b64encode(
                        json.dumps(dashboard_spec).encode("utf-8")
                    ).decode("utf-8"),
            "format": "AUTO",
            "overwrite": "true"
        }
        return self.make_request("post", f"/workspace/import", json=request_data)

    def get_dashboard_resource_id(self, dashboard_name: str,dashboard_folder: str):
        return self.make_request("get", f"/workspace/get-status", params={"path": f"{dashboard_folder}/{dashboard_name}.lvdash.json"}).json().get("resource_id")


    def publish_dashboard(self, warehouse_name: str,dashboard_folder: str,dashboard_name: str):
        warehouse_id = self.get_warehouse_by_name(warehouse_name)["id"]

        response = self.make_request("get", f"/workspace/get-status", params={"path": f"{dashboard_folder}/{dashboard_name}.lvdash.json"})

        if response.status_code == 200:
            dashboard_resource_id = response.json().get("resource_id")
            if dashboard_resource_id is not None:
                response_pub = self.make_request("post", f"/lakeview/dashboards/{dashboard_resource_id}/published", 
                   json={
                        "embed_credentials": True,
                        "warehouse_id": f"{warehouse_id}"
                   })
                if response_pub.status_code != 200:
                    raise Exception(f"Failed to publish dashboard: {response_pub.text}")        
        
        if response.status_code != 200:
            raise Exception(f"Failed to publish dashboard: {response.text}")
        return response.json()
    
    def create_and_publish_dashboard(self, warehouse_name: str, dashboard_spec: str,dashboard_folder: str,dashboard_name: str):
        self.create_dashboard(dashboard_spec=dashboard_spec,dashboard_folder=dashboard_folder,dashboard_name=dashboard_name)
        return self.publish_dashboard(warehouse_name=warehouse_name,dashboard_folder=dashboard_folder,dashboard_name=dashboard_name)
        