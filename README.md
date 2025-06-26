# 🧰 GCP Dataform CLI Tool (Fetch & Push)

This tool provides a command-line interface (CLI) to **fetch** and **push** Dataform repository content from/to **Google Cloud Platform**. It runs inside a Docker container and uses the [Dataform API](https://cloud.google.com/dataform/docs/reference/rest).

---

## 🚀 Features

- ✅ Fetch all files from GCP Dataform repository workspaces
- ✅ Push local Dataform code to a GCP workspace
- ✅ Fully Dockerized CLI
- ✅ Uses Service Account authentication

---

## 📦 Requirements

- Docker installed
- A Google Cloud project with:
  - **Dataform API enabled**
  - A **Dataform repository**
  - A **Service Account JSON key** with at least:
    - `Dataform Viewer`
    - `Dataform Editor` (for push)
- (Optional) Python & pip to build locally

---

## 🛠️ Build the Docker Image

```bash
docker build -t dataform-cli .
````

---

## 🔐 Authentication

Place your Service Account JSON key in your working directory (e.g., `sa.json`).

---

## 📂 Directory Structure

```
.
├── Dockerfile
├── main.py
├── requirements.txt
├── sa.json              # your GCP service account credentials
└── your-local-code/     # folder with Dataform code to push
```

---

## 📥 Fetch Mode

Fetches files from all workspaces in the Dataform repository.

```bash
docker run --rm \
  -v $PWD:/app \
  -v $PWD/sa.json:/app/sa.json \
  dataform-cli \
  --project <your-project-id> \
  --location <region> \
  --repo <repository-id> \
  --sa-file /app/sa.json
```

---

## 📤 Push Mode

Pushes all files from a local directory to a specified workspace in your Dataform repo.

```bash
docker run --rm \
  -v $PWD:/app \
  -v $PWD/your-local-code:/code \
  -v $PWD/sa.json:/app/sa.json \
  dataform-cli \
  --project <your-project-id> \
  --location <region> \
  --repo <repository-id> \
  --sa-file /app/sa.json \
  --push-dir /code \
  --workspace cli-workspace
```

> ℹ️ `--workspace` is optional; defaults to `cli-workspace`

---

## 📄 CLI Arguments

| Argument      | Required | Description                                                |
| ------------- | -------- | ---------------------------------------------------------- |
| `--project`   | ✅        | GCP Project ID                                             |
| `--location`  | ✅        | GCP Region (e.g., `us-central1`)                           |
| `--repo`      | ✅        | Dataform Repository ID                                     |
| `--sa-file`   | ✅        | Path to Service Account JSON                               |
| `--push-dir`  | ❌        | Local directory to push to the workspace                   |
| `--workspace` | ❌        | Workspace ID to use for pushing (default: `cli-workspace`) |

---

## 🧪 Examples

### Fetch all files:

```bash
docker build --tag surquest/dataform-cli:dev --file Dockerfile --target base .

docker run -it --rm \
  -v $PWD/src/surquest/GCP/dataform-cli:/app/dataform-cli \
  -v $PWD/credentials/PROD/sa.keyfile.json:/app/credentials/sa.keyfile.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/sa.keyfile.json \
  surquest/dataform-cli:dev \
  python /app/dataform-cli/main.py \
  --project analytics-data-mart \
  --location us-central1 \
  --repo etl--user-acquisition \
  --sa-file /app/credentials/sa.keyfile.json
```

### Push code:

```bash
docker run --rm -v $PWD:/app -v $PWD/my-code:/code -v $PWD/sa.json:/app/sa.json dataform-cli \
  --project my-project \
  --location us-central1 \
  --repo my-repo \
  --sa-file /app/sa.json \
  --push-dir /code
```

---

## 📌 Notes

* This tool **does not commit or compile** workspaces after push (coming soon).
* Works with **v1beta1** of the Dataform API.

---

## 📄 License

MIT License

---

## 🤝 Contributions

PRs welcome! Please ensure you test before submitting changes.
