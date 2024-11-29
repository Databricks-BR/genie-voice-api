# Databricks notebook source
import requests
import json
import time
import numpy as np  # for nice rendering
import pandas as pd  # for nice rendering
import re  # for nice rendering

# Temp helper waiting for the python SDK to be updated with apps
class LakehouseAppHelper:
    def __init__(self):
        from databricks import sdk

        self.host = sdk.config.Config().host
        # self.host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None)

    def get_headers(self):
        from databricks import sdk

        return sdk.config.Config().authenticate()

    def list(self):
        json = requests.get(
            f"{self.host}/api/2.0/apps", headers=self.get_headers()
        ).json()

        # now render it nicely
        df = pd.DataFrame.from_dict(json["apps"], orient="columns")
        df["state"] = df["compute_status"].apply(lambda x: x["state"])
        df["compute_status message"] = df["compute_status"].apply(lambda x: x["message"])
        df.drop("compute_status", axis=1, inplace=True)
        df = df[["name", "state", "compute_status message", "create_time", "url"]]
        df["logz"] = df["url"].apply(lambda x: "" if x == "" else x + "/logz")
        html = df.to_html(index=False)
        html = re.sub(
            r"https://((\w|-|\.)+)\.databricksapps\.com/logz",
            r'<a href="https://\1.databricksapps.com/logz">Logz</a>',
            html,
        )
        html = re.sub(
            r"(<td>)(https://((\w|-|\.)+)\.databricksapps\.com)",
            r'\1<a href="\2">Link</a>',
            html,
        )
        html = re.sub(
            r"(<td>)(ERROR)(</td>)", r'\1<span style="color:red">\2</span>\3', html
        )
        html = re.sub(
            r"(<td>)(RUNNING)(</td>)", r'\1<span style="color:green">\2</span>\3', html
        )
        html = (
            "<style>.dataframe tbody td { text-align: left; font-size: 14 } .dataframe th { text-align: left; font-size: 14 }</style>"
            + html
        )
        displayHTML(html)

    def create(self, app_name, app_description="This app does something"):
        exists = requests.get(
            f"{self.host}/api/2.0/apps/{app_name}",
            headers=self.get_headers()
        )

        if exists.status_code == 200:
            print("Application already exists")
            return exists.json()

        result = requests.post(
            f"{self.host}/api/2.0/apps",
            headers=self.get_headers(),
            json={"name": app_name, "spec": {"description": app_description}},
        ).json()

        if "error_code" in result:
            if result["error_code"] == "ALREADY_EXISTS":
                print("Application already exists")
            else:
                raise Exception(result)

        # The create API is async, so we need to poll until it's ready.

        response = requests.get(
            f"{self.host}/api/2.0/apps/{app_name}",
            headers=self.get_headers(),
        ).json()
        print(f"Waiting for app {app_name} to be ready...")
        while "ACTIVE" not in self.get_app_details(app_name)["compute_status"]["state"]:
            time.sleep(2)
        print(f"App {app_name} successfully created")
        return self.get_app_details(app_name)

    def add_dependencies(self, app_name, dependencies, overwrite=True):
        if not overwrite:
            existing_dependencies = self.get_app_details(app_name).get('dependencies')
            dependencies.extend(existing_dependencies) if existing_dependencies is not None else None
        
        result = requests.patch(
            f"{self.host}/api/2.0/apps/{app_name}",
            headers=self.get_headers(),
            json={
                "name": app_name,
                "resources": dependencies
            },
        ).json()
        if "error_code" in result:
            raise Exception(result)

        # The create API is async, so we need to poll until it's ready.
        for _ in range(10):
            time.sleep(5)
            response = requests.get(
                f"{self.host}/api/2.0/apps/{app_name}",
                headers=self.get_headers(),
            ).json()
            #print(response)
            if response["compute_status"]["state"] != "CREATING":
                break
        return response

    def deploy(self, app_name, source_code_path):
        # Deploy starts the pod, downloads the source code, install necessary dependencies, and starts the app.
        response = requests.post(
            f"{self.host}/api/2.0/apps/{app_name}/deployments",
            headers=self.get_headers(),
            json={"source_code_path": source_code_path},
        ).json()
        deployment_id = response["deployment_id"]

        response = requests.get(
                f"{self.host}/api/2.0/apps/{app_name}/deployments/{deployment_id}",
                headers=self.get_headers(),
            ).json()
        
        print(f"Waiting for app {app_name} to be ready...")
        while "RUNNING" not in self.get_app_details(app_name)["compute_status"]["state"]:
            time.sleep(5)
        print(f"App {app_name} successfully deployed")
        return response

    def get_app_details(self, app_name):
        url = self.host + f"/api/2.0/apps/{app_name}"
        return requests.get(url, headers=self.get_headers()).json()

    def details(self, app_name):
        json = self.get_app_details(app_name)
        # now render it nicely
        df = pd.DataFrame.from_dict(json, orient="index")
        html = df.to_html(header=False)
        html = re.sub(
            r"(<td>)(https://((\w|-|\.)+)\.databricksapps\.com)",
            r'\1<a href="\2">\2</a>',
            html,
        )
        html = (
            "<style>.dataframe tbody td { text-align: left; font-size: 14 } .dataframe th { text-align: left; font-size: 14 }</style>"
            + html
        )
        displayHTML(html)

    def delete(self, app_name):
        url = self.host + f"/api/2.0/apps/{app_name}"
        json = self.get_app_details(app_name)
        if "error_code" in json:
            print(f"App {app_name} doesn't exist {json}")
            return
        print(f"Waiting for the app {app_name} to be deleted...")
        _ = requests.delete(url, headers=self.get_headers()).json()
        while "error_code" not in self.get_app_details(app_name):
            time.sleep(2)
        print(f"App {app_name} successfully deleted")
