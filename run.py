from src.surquest.GCP.dataform_cli.handlers.pull_handler import PullHandler
from src.surquest.GCP.dataform_cli.handlers.gitignore_handler import GitignoreHandler

project_id="analytics-data-mart"
region="us-central1"
repository_id="etl--user-acquisition"
workspace_id="dev--workspace"

workspace_path = PullHandler.get_workspace_path(
    project_id=project_id,
    region=region,
    repository_id=repository_id,
    workspace_id=workspace_id
)

print(workspace_path)

empty_dirs, nonempty_dirs = PullHandler.get_workspace_directories(
    workspace_path=workspace_path,
    gitignore_handler=GitignoreHandler(gitignore_path=".gitignore")
)

print(empty_dirs)

files = PullHandler.get_workspace_files(
    workspace_path=workspace_path,
    gitignore_handler=GitignoreHandler(gitignore_path=".gitignore")
)

print(files)

trully_empty = PullHandler.get_empty_directories(empty_dirs=empty_dirs, files=files)
print("Trully empty:", trully_empty)