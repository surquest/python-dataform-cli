# Dataform CLI

## 🎯 Objective & Motivation

`dataform_cli` is a lightweight Python-based command-line interface (CLI) designed to simplify **file synchronization between local directories and Google Cloud Dataform workspaces**. The primary goal is to accelerate development workflows by allowing easy `push` and `pull` operations of `.sqlx`, `.js`, and other source files while respecting `.gitignore` rules.

It helps developers:
- Avoid repetitive UI interactions.
- Manage versioning consistently with `.gitignore`.
- Automate CI/CD tasks for Dataform repositories from on-premise hosted Gitlab 

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
````

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

