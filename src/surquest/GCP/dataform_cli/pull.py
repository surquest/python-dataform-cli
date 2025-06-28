import os
from google.api_core import exceptions
from .handlers.gitignore_handler import GitignoreHandler
from .handlers.pull_handler import PullHandler
from .logger import get_fixed_width_logger


def pull(project_id, region, repository_id, workspace_id, target_dir, logger=get_fixed_width_logger(name="pullLogger")):
    """
    Downloads all files from a Google Cloud Dataform workspace to a local directory,
    excluding files and directories specified in a `.gitignore` file if present in the workspace.

    This function mirrors the workspace content into a local directory, preserving the folder structure
    and ignoring any paths that match the .gitignore rules pulled from the workspace.

    Args:
        project_id (str): The Google Cloud project ID.
        region (str): The region of the Dataform repository.
        repository_id (str): The ID of the Dataform repository.
        workspace_id (str): The ID of the Dataform workspace.
        target_dir (str): The path to the local directory where files will be saved.
        logger (logging.Logger): Logger instance for structured logging. Defaults to fixed-width logger.
    """
    workspace_path = PullHandler.dataform_client.workspace_path(
        project_id, region, repository_id, workspace_id
    )

    logger.info(f"Pulling files from workspace: {workspace_path}")
    target_dir_abs = os.path.abspath(target_dir)
    logger.info(f"Target directory: {target_dir_abs}")

    if not os.path.exists(target_dir):
        logger.info("Creating target directory...")
        os.makedirs(target_dir)

    # Attempt to pull .gitignore from workspace
    gitignore_handler = None
    gitignore_path = os.path.join(target_dir, ".gitignore")

    try:
        logger.debug("Fetching .gitignore from workspace...")
        gitignore_content = PullHandler.pull_file(
            file_path=".gitignore",
            workspace_path=workspace_path
        )

        PullHandler.write_file(
            file_path=gitignore_path,
            file_contents=gitignore_content
        )

        gitignore_handler = GitignoreHandler(gitignore_path=gitignore_path)
        logger.info(".gitignore file found and saved")

    except exceptions.NotFound:
        logger.warning("No .gitignore file found in workspace. Proceeding without ignore rules.")

    # List and optionally filter workspace files
    workspace_files = PullHandler.get_workspace_files(
        workspace_path=workspace_path,
        gitignore_handler=gitignore_handler
    )

    logger.info(f"Found {len(workspace_files)} files in workspace")

    for file_path in workspace_files:
        logger.info(f"Pulling: {file_path}")
        try:
            file_content = PullHandler.pull_file(
                file_path=file_path,
                workspace_path=workspace_path
            )

            local_file_path = os.path.join(target_dir, file_path)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            PullHandler.write_file(
                file_path=local_file_path,
                file_contents=file_content
            )

            logger.debug(f"Saved to: {local_file_path}")

        except Exception as e:
            logger.error(f"Failed to pull {file_path}: {e}")

    logger.info("Pull completed successfully.")
