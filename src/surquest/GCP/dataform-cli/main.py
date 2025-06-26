# main.py

import argparse
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_dataform_service(sa_file):
    credentials = service_account.Credentials.from_service_account_file(sa_file, scopes=SCOPES)
    service = build("dataform", "v1beta1", credentials=credentials)
    return service

def list_workspaces(service, project, location, repository_id):
    parent = f"projects/{project}/locations/{location}/repositories/{repository_id}"
    workspaces = []
    request = service.projects().locations().repositories().workspaces().list(parent=parent)
    while request is not None:
        response = request.execute()
        workspaces.extend(response.get("workspaces", []))
        request = service.projects().locations().repositories().workspaces().list_next(
            previous_request=request, previous_response=response)
    return workspaces

def list_files_in_workspace(service, workspace_name):
    files = []
    request = service.projects().locations().repositories().workspaces().listFiles(name=workspace_name)
    response = request.execute()
    files.extend(response.get("files", []))
    return files

def read_file(service, workspace_name, path):
    request = service.projects().locations().repositories().workspaces().readFile(
        workspace=workspace_name,
        path=path
    )
    response = request.execute()
    return response.get("fileContents", "")

def write_file(service, workspace_name, path, content):
    body = {
        "path": path,
        "contents": content
    }
    request = service.projects().locations().repositories().workspaces().writeFile(
        workspace=workspace_name,
        body=body
    )
    return request.execute()

def create_workspace_if_missing(service, project, location, repo, workspace_id):
    name = f"projects/{project}/locations/{location}/repositories/{repo}/workspaces/{workspace_id}"
    try:
        return service.projects().locations().repositories().workspaces().get(name=name).execute()
    except:
        parent = f"projects/{project}/locations/{location}/repositories/{repo}"
        body = {
            "name": name,
            "workspaceId": workspace_id
        }
        return service.projects().locations().repositories().workspaces().create(
            parent=parent, body={}, workspaceId=workspace_id
        ).execute()

def fetch_repository_content(project, location, repository_id, sa_file):
    service = get_dataform_service(sa_file)
    workspaces = list_workspaces(service, project, location, repository_id)
    for workspace in workspaces:
        name = workspace["name"]
        print(f"\n=== Files in workspace: {name} ===")
        files = list_files_in_workspace(service, name)
        for file in files:
            path = file.get("path")
            print(f"\nFile: {path}")
            content = read_file(service, name, path)
            print(content)

def push_repository_content(project, location, repository_id, sa_file, local_path, workspace_id):
    service = get_dataform_service(sa_file)
    create_workspace_if_missing(service, project, location, repository_id, workspace_id)
    workspace_name = f"projects/{project}/locations/{location}/repositories/{repository_id}/workspaces/{workspace_id}"

    for root, dirs, files in os.walk(local_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, start=local_path)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Pushing file: {rel_path}")
            write_file(service, workspace_name, rel_path, content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch or Push GCP Dataform repository content.")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--location", required=True, help="GCP region (e.g. us-central1)")
    parser.add_argument("--repo", required=True, help="Dataform repository ID")
    parser.add_argument("--sa-file", required=True, help="Path to service account JSON file")
    parser.add_argument("--push-dir", help="Local directory to push to Dataform")
    parser.add_argument("--workspace", default="cli-workspace", help="Workspace ID for push operations")
    
    args = parser.parse_args()

    if args.push_dir:
        push_repository_content(args.project, args.location, args.repo, args.sa_file, args.push_dir, args.workspace)
    else:
        fetch_repository_content(args.project, args.location, args.repo, args.sa_file)
