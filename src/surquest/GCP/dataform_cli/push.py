import os
from google.api_core import exceptions
from .handlers.gitignore_handler import GitignoreHandler
from .handlers.pull_handler import PullHandler
from .handlers.push_handler import PushHandler
from .logger import get_fixed_width_logger


def push(
        project_id,
        region,
        repository_id,
        workspace_id,
        source_dir,
        delete_remote_files=True,
        autocommit=True,
        autopush=True,
        logger=get_fixed_width_logger(name="pushLogger")
    ):
    """
    Pushes all files from a local source directory to a specified Google Cloud Dataform workspace,
    while respecting ignore rules defined in a .gitignore file.

    Files and directories listed in the .gitignore file will be excluded from the upload.
    Optionally supports automatic commit and push operations, and can also delete files
    from the remote workspace that no longer exist locally.

    Args:
        project_id (str): The Google Cloud project ID where the Dataform repository resides.
        region (str): The region in which the Dataform repository is hosted.
        repository_id (str): The unique identifier of the Dataform repository.
        workspace_id (str): The ID of the workspace within the repository to push to.
        source_dir (str): The path to the local directory whose contents will be pushed.
        delete_remote_files (bool): If True, removes files from the remote workspace
            that are not present in the local source directory. Defaults to True.
        autocommit (bool): If True, automatically commits the changes after pushing. Defaults to True.
        autopush (bool): If True, automatically pushes the committed changes to the remote repository. Defaults to True.
        logger (logging.Logger): Logger instance for structured logging. A default fixed-width logger is used if not provided.
    """
    logger.info("Determining workspace path...")
    workspace_path = PushHandler.get_workspace_path(project_id, region, repository_id, workspace_id)

    logger.info("Scanning local files...")
    local_files = PushHandler.get_local_files(source_dir)

    logger.info("Retrieving remote files...")
    try:
        remote_files = PullHandler.get_workspace_files(
            workspace_path=workspace_path,
            gitignore_handler=GitignoreHandler(".gitignore")
        )
    except exceptions.GoogleAPICallError as e:
        logger.error(f"Failed to list remote files: {e}")
        remote_files = []

    logger.info(f"{len(local_files)} local files, {len(remote_files)} remote files")

    # Push local files
    for relative_path in local_files:
        local_path = os.path.join(source_dir, relative_path)
        logger.info(f"Pushing file: {relative_path}")
        PushHandler.write_file(local_path, relative_path, workspace_path)

    # Delete remote files not present locally
    if delete_remote_files:
        files_to_delete = set(remote_files) - set(local_files)
        for file_path in files_to_delete:
            logger.info(f"Deleting remote file: {file_path}")
            PushHandler.remove_file(file_path, workspace_path)

    # Get directories from remote repository
    remote_empty_dirs, remote_nonempty_dirs = PullHandler.get_workspace_directories(
        workspace_path=workspace_path,
        gitignore_handler=GitignoreHandler(gitignore_path=".gitignore")
    )
    # Ger files from remote repository
    remote_files = PullHandler.get_workspace_files(
        workspace_path=workspace_path,
        gitignore_handler=GitignoreHandler(gitignore_path=".gitignore")
    )
    # Get trully empty dirs:
    trully_empty_dirs = PullHandler.get_empty_directories(
        empty_dirs=remote_empty_dirs,
        files=remote_files
    )

    if len(trully_empty_dirs) > 0:
        logger.info(f"Deleting empty directories: count of trully directories is {len(trully_empty_dirs)}")
        for empty_dir in trully_empty_dirs:
            logger.info(f"Deleting trully empty directory: {empty_dir}")
            PushHandler.remove_directory(empty_dir, workspace_path)

    # Commit changes if enabled
    if autocommit:
        logger.info("Committing workspace changes...")
        PushHandler.commit_workspace_changes(workspace_path, message="Automated push from CLI")

    # Push commits if enabled
    if autopush:
        logger.info("Pushing git commits...")
        PushHandler.push_git_commits(workspace_path)

    logger.info("Push completed successfully.")
