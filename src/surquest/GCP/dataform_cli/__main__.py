import argparse
import os
import logging
from google.cloud import dataform_v1
from google.api_core import exceptions

from .handlers.gitignore_handler import GitignoreHandler
from .handlers.pull_handler import PullHandler

# The 'pathspec' library is used for .gitignore style matching.
# Please install it using: pip install pathspec
try:
    import pathspec
except ImportError:
    logging.error("Error: 'pathspec' library not found.")
    logging.error("Please install it using: pip install pathspec")
    logging.info("Example: pip install pathspec")
    logging.info("Example: pip install -e .[dev] # If installing from the repository")
    exit(1)


# def create_dataform_client():
#     """Creates and returns a Dataform API client."""
#     try:
#         return dataform_v1.DataformClient()
#     except Exception as e:
#         print(f"Error creating Dataform client: {e}")
#         print("Please ensure you have authenticated with Google Cloud CLI and have the necessary permissions.")
#         exit(1)

# def _pull_recursively(client, workspace_path, remote_dir_path, local_dir_path, gitignore_spec):
#     """
#     A helper function to recursively pull files and directories.
#     It respects the provided .gitignore spec.

#     Args:
#         client: The Dataform client.
#         workspace_path: The full path to the Dataform workspace.
#         remote_dir_path: The current directory path within the Dataform workspace.
#         local_dir_path: The corresponding local directory path.
#         gitignore_spec: The compiled pathspec from the .gitignore file.
#     """
#     try:
#         # Query contents of the current remote directory
        
#         # Initialize request argument(s)
#         request = dataform_v1.QueryDirectoryContentsRequest(
#             workspace=workspace_path,
#             path=remote_dir_path
#         )

#         response = client.query_directory_contents(request=request)

#         for entry in response.directory_entries:
#             entry_name = entry.file or entry.directory
#             if not entry_name:
#                 continue

#             full_remote_path = os.path.join(remote_dir_path, entry_name)
#             full_local_path = os.path.join(local_dir_path, entry_name)

#             # Check if the path should be ignored. We add a trailing slash to directories
#             # to correctly match against gitignore patterns like `dir/`.
#             check_path = full_remote_path + "/" if entry.directory else full_remote_path
#             if gitignore_spec and gitignore_spec.match_file(check_path):
#                 print(f"  - Ignoring: {full_remote_path}")
#                 continue

#             if entry.directory:
#                 print(f"  - Creating directory: {full_remote_path}")
#                 os.makedirs(full_local_path, exist_ok=True)
#                 # Recursive call for the subdirectory
#                 _pull_recursively(
#                     client, workspace_path, f"{full_remote_path}", full_local_path, gitignore_spec
#                 )
#             else:  # It's a file
#                 print(f"  - Pulling file: {full_remote_path}")
                
#                 request = dataform_v1.ReadFileRequest(
#                     workspace=workspace_path,
#                     path=full_remote_path
#                 )

#                 # Make the request
#                 read_file_response = client.read_file(request=request)
                
#                 with open(full_local_path, "wb") as f:
#                     f.write(read_file_response.file_contents)
#                 print(f"    - Saved to: {full_local_path}")

#     except Exception as e:
#         print(f"An error occurred while pulling '{remote_dir_path}': {e}")


def pull_files(project_id, region, repository_id, workspace_id, target_dir):
    """
    Pulls all files from a Dataform workspace to a local directory,
    excluding files and directories specified in a .gitignore file.

    Args:
        project_id: The Google Cloud project ID.
        region: The region of the Dataform repository.
        repository_id: The ID of the Dataform repository.
        workspace_id: The ID of the Dataform workspace.
        target_dir: The local directory to save the files to.
    """

    workspace_path = PullHandler.dataform_client.workspace_path(project_id, region, repository_id, workspace_id)

    logging.info(f"Pulling files from workspace: {workspace_path}")
    logging.info(f"Target directory: {os.path.abspath(target_dir)}")

    logging.info(f"Creating the target directory: {os.path.abspath(target_dir)} if not exists")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


    logging.debug(f"Fething the gitignore from Google Cloud Dataform Repository")

    has_remote_gitignore = False
    gitignore_handler = None
    try:
        gitignore_file_content = PullHandler.pull_file(
            file_path=".gitignore",
            workspace_path=workspace_path
        )

        PullHandler.write_file(
            file_path=os.path.join(target_dir, ".gitignore"),
            file_contents=gitignore_file_content
        )

        has_remote_gitignore = True
        gitignore_handler = GitignoreHandler(
            gitignore_path=os.path.join(target_dir, ".gitignore")
        )

    except exceptions.NotFound as err:
        has_remote_gitignore = False
        logging.warning(f"No .gitignore file found")

    workspace_files = PullHandler.get_workspace_files(
        workspace_path=workspace_path,
        gitignore_handler=gitignore_handler
    )

    logging.info(f"Files in workspace: {workspace_files}")

    for workspace_file in workspace_files:
        
        logging.info(f"Pulling file: {workspace_file}")

        file_content = PullHandler.pull_file(
            file_path=workspace_file,
            workspace_path=workspace_path
        )

        logging.info(f" - file content pulled")

        local_file_path = os.path.join(target_dir, workspace_file)
        
        logging.info(f" - file path: {local_file_path}")
        
        PullHandler.write_file(
            file_path=os.path.join(target_dir, workspace_file),
            file_contents=file_content
        )

        logging.info(f" - file saved")

def push_files(project_id, region, repository_id, workspace_id, source_dir, author_name, author_email):
    """
    Pushes files from a local directory to a Dataform workspace and commits them.

    Args:
        project_id: The Google Cloud project ID.
        region: The region of the Dataform repository.
        repository_id: The ID of the Dataform repository.
        workspace_id: The ID of the Dataform workspace.
        source_dir: The local directory containing the files to push.
        author_name: The name of the commit author.
        author_email: The email of the commit author.
    """
    client = create_dataform_client()
    workspace_path = client.workspace_path(project_id, region, repository_id, workspace_id)

    print(f"Pushing files to workspace: {workspace_path}")

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' not found.")
        return

    try:
        # Walk through the local directory and push files
        for root, _, files in os.walk(source_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                
                # Get the relative path to be used in the Dataform workspace
                relative_path = os.path.relpath(local_file_path, source_dir)
                
                print(f"  - Pushing file: {relative_path}")

                with open(local_file_path, "rb") as f:
                    file_contents = f.read()

                # Write the file to the Dataform workspace
                client.write_file(
                    name=workspace_path,
                    path=relative_path,
                    contents=file_contents
                )
        
        print("\nAll files pushed. Now committing changes...")

        # Commit the changes to the workspace
        author = dataform_v1.CommitAuthor(name=author_name, email_address=author_email)
        client.commit_workspace_changes(
            name=workspace_path,
            author=author,
            commit_message="Pushed files from local CLI"
        )
        
        print("Commit successful. Push complete.")

    except exceptions.NotFound:
        print(f"Error: Workspace not found at '{workspace_path}'")
        print("Please check your project ID, region, repository ID, and workspace ID.")
    except Exception as e:
        print(f"An error occurred during the push operation: {e}")


def main():
    """Main function to parse arguments and call the appropriate functions."""
    parser = argparse.ArgumentParser(description="A CLI tool to interact with Google Cloud Dataform.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- Logging level -- 
    parser.add_argument("--log-level", default="INFO", help="Set the logging level (default: INFO)")

    # --- Pull Command ---
    parser_pull = subparsers.add_parser("pull", help="Pull files from a Dataform repository.")
    parser_pull.add_argument("--project-id", required=True, help="Your Google Cloud project ID.")
    parser_pull.add_argument("--region", required=True, help="The region of your Dataform repository (e.g., 'us-central1').")
    parser_pull.add_argument("--repository-id", required=True, help="The ID of your Dataform repository.")
    parser_pull.add_argument("--workspace-id", required=True, help="The ID of your Dataform workspace.")
    parser_pull.add_argument("--target-dir", default=".", help="The local directory to pull files into (default: current directory).")

    # --- Push Command ---
    parser_push = subparsers.add_parser("push", help="Push files to a Dataform repository.")
    parser_push.add_argument("--project-id", required=True, help="Your Google Cloud project ID.")
    parser_push.add_argument("--region", required=True, help="The region of your Dataform repository (e.g., 'us-central1').")
    parser_push.add_argument("--repository-id", required=True, help="The ID of your Dataform repository.")
    parser_push.add_argument("--workspace-id", required=True, help="The ID of your Dataform workspace.")
    parser_push.add_argument("--source-dir", default=".", help="The local directory to push files from (default: current directory).")
    parser_push.add_argument("--author-name", required=True, help="The name for the commit author.")
    parser_push.add_argument("--author-email", required=True, help="The email for the commit author.")

    # Set the logging level
    logging.basicConfig(level=parser.parse_args().log_level)

    args = parser.parse_args()

    if args.command == "pull":
        pull_files(args.project_id, args.region, args.repository_id, args.workspace_id, args.target_dir)
    elif args.command == "push":
        push_files(args.project_id, args.region, args.repository_id, args.workspace_id, args.source_dir, args.author_name, args.author_email)

if __name__ == "__main__":
    main()
