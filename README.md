# Dataform CLI

## 🎯 Objective & Motivation

`dataform_cli` is a lightweight Python-based command-line interface (CLI) designed to simplify **file synchronization between local directories and Google Cloud Dataform workspaces**. The primary goal is to accelerate development workflows by allowing easy `push` and `pull` operations of `.sqlx`, `.js`, and other source files while respecting `.gitignore` rules.

It helps developers:
- Avoid repetitive UI interactions.
- Manage versioning consistently with `.gitignore`.
- Automate CI/CD tasks for Dataform repositories.

---

## 🚀 Features

- ✅ Push local files to a specified Dataform workspace.
- ✅ Pull files from a Dataform workspace to a local directory.
- ✅ Support for `.gitignore` filtering.
- ✅ Optional automatic `commit` and `git push` on file upload.
- ✅ Fixed-width logging with timestamps and log levels.
- ✅ Easy integration with Python projects or automation scripts.

---

## 💻 Usage Examples

### Push files to Dataform

```bash
python -m surquest.GCP.dataform_cli push \
  --project-id=my-gcp-project \
  --region=europe-west1 \
  --repository-id=my-repo \
  --workspace-id=dev \
  --source-dir=./src
```

Optional flags:

* `--no-delete-remote-files`: Do not remove remote files not present locally.
* `--no-autocommit`: Skip auto-committing workspace changes.
* `--no-autopush`: Skip pushing git commits.

---

### Pull files from Dataform

```bash
python -m surquest.GCP.dataform_cli pull \
  --project-id=my-gcp-project \
  --region=europe-west1 \
  --repository-id=my-repo \
  --workspace-id=dev \
  --target-dir=./local_workspace
```

---

## 🐳 Using the CLI via Docker

You can run the CLI inside a Docker container, mounting your local source or target directory as a volume, and passing your Google credentials via an environment variable.

```bash
docker run --rm -it \
  -v /path/to/local/source:/app/source \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/creds.json \
  -v /path/to/your/creds.json:/app/creds.json:ro \
  your-docker-image-name \
  python -m surquest.GCP.dataform_cli push \
    --project-id=my-gcp-project \
    --region=europe-west1 \
    --repository-id=my-repo \
    --workspace-id=dev \
    --source-dir=/app/source
```

Similarly, for pulling files:

```bash
docker run --rm -it \
  -v /path/to/local/target:/app/target \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/creds.json \
  -v /path/to/your/creds.json:/app/creds.json:ro \
  your-docker-image-name \
  python -m surquest.GCP.dataform_cli pull \
    --project-id=my-gcp-project \
    --region=europe-west1 \
    --repository-id=my-repo \
    --workspace-id=dev \
    --target-dir=/app/target
```

**Notes:**

* Replace `/path/to/local/source` and `/path/to/local/target` with your actual local paths.
* The service account key JSON file is mounted inside the container at `/app/creds.json`.
* The `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to this file for authentication.
* `your-docker-image-name` should be replaced with your built Docker image tag.

---

## 🛠 Requirements

* Python 3.8+
* `google-cloud-dataform`
* Service account or user credentials with access to the Dataform API.

---

## 📬 Contact & Support

For issues, improvements, or collaboration, please contact:

**Michal Švarc**
✉️ \[[michal.svarc@surquest.com](mailto:michal.svarc@surquest.com)]
📞 +420 724 031 631
