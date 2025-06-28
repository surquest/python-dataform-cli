import argparse
import sys
from .push import push
from .pull import pull
from .logger import get_fixed_width_logger

def main():
    logger = get_fixed_width_logger()

    parser = argparse.ArgumentParser(
        description="Dataform CLI for pushing and pulling workspace files."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Push command parser
    push_parser = subparsers.add_parser("push", help="Push local files to Dataform workspace.")
    push_parser.add_argument("--project-id", required=True, help="Google Cloud project ID")
    push_parser.add_argument("--region", required=True, help="Region of the Dataform repository")
    push_parser.add_argument("--repository-id", required=True, help="ID of the Dataform repository")
    push_parser.add_argument("--workspace-id", required=True, help="ID of the Dataform workspace")
    push_parser.add_argument("--source-dir", required=True, help="Path to local source directory")
    push_parser.add_argument("--no-delete-remote-files", action="store_true", help="Do not delete remote files not in local source")
    push_parser.add_argument("--no-autocommit", action="store_true", help="Do not auto-commit after push")
    push_parser.add_argument("--no-autopush", action="store_true", help="Do not auto-push git commits")

    # Pull command parser
    pull_parser = subparsers.add_parser("pull", help="Pull files from Dataform workspace to local directory.")
    pull_parser.add_argument("--project-id", required=True, help="Google Cloud project ID")
    pull_parser.add_argument("--region", required=True, help="Region of the Dataform repository")
    pull_parser.add_argument("--repository-id", required=True, help="ID of the Dataform repository")
    pull_parser.add_argument("--workspace-id", required=True, help="ID of the Dataform workspace")
    pull_parser.add_argument("--target-dir", required=True, help="Path to local target directory")

    args = parser.parse_args()

    if args.command == "push":
        logger.info("Starting push operation...")
        push(
            project_id=args.project_id,
            region=args.region,
            repository_id=args.repository_id,
            workspace_id=args.workspace_id,
            source_dir=args.source_dir,
            delete_remote_files=not args.no_delete_remote_files,
            autocommit=not args.no_autocommit,
            autopush=not args.no_autopush,
            logger=logger
        )

    elif args.command == "pull":
        logger.info("Starting pull operation...")
        pull(
            project_id=args.project_id,
            region=args.region,
            repository_id=args.repository_id,
            workspace_id=args.workspace_id,
            target_dir=args.target_dir,
            logger=logger
        )

    else:
        logger.error("Unknown command")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
