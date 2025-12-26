# cognitoidp-local
A lightweight, persistent Cognito mock server using Moto with file-based state persistence.

![alt text](https://img.shields.io/docker/image-size/usermalikhan/cognitoidp-local/latest)

![alt text](https://img.shields.io/badge/license-Apache%202-blue)

![alt text](https://img.shields.io/badge/python-3.9-yellow)
![alt text](https://img.shields.io/badge/python-3.10-yellow)
![alt text](https://img.shields.io/badge/python-3.11-yellow)
![alt text](https://img.shields.io/badge/python-3.12-yellow)
![alt text](https://img.shields.io/badge/python-3.13-yellow)

This is a wrapper around the moto library in a lightweight Docker container and adds a custom persistence layer that
auto-saves your data to disk.

## ✨ Features

💾 Persistent.
⚡ Blazing Fast.
🆓 Free & Open.
🐳 Docker Ready.

Cryptography Support: Includes patches to correctly serialize RSA keys used for JWT signing.

🔁 Auto-Save: Background thread saves state every interval and handles graceful shutdowns (SIGTERM).

It supports multiple regions and can be configured to use a custom data directory.

## 🚀 Quick Start

#### Using Docker Compose **(Recommended)**
Add this to your docker-compose.yml.

    services:
      cognito:
        image: usermalikhan/cognitoidp-local:latest
        container_name: cognitoidp-local
        ports:
          - "4566:4566"
        volumes:
          - ./cognito-data:/data
        environment:
          - AWS_DEFAULT_REGION=eu-central-1
          - PORT=4566


### Using Docker CLI

    docker run -d \
      -p 4566:4566 \
      -v $(pwd)/cognito-data:/data \
      --region eu-central-1 \
      --name cognitoidp-local \
      usermalikhan/cognitoidp-local:latest

## 🛠 How It Works

This project is a Python wrapper around the moto[server] library.

The Engine: It uses moto's ThreadedMotoServer to handle AWS API requests.

The Patch: It injects a custom serializer into Python's pickle module using copyreg.
This allows it to save complex C-based cryptography objects (like RSA Private Keys) which standard Python cannot pickle.

The Loop: A background thread monitors the Moto backend object. Every interval (or on Docker shutdown signals),
it dumps the entire memory state to a file (/data/cognito.db).

The Restoration: On startup, it checks for the database file and injects the data back into Moto's memory before the
server starts accepting requests.

## 🔌 Connecting to It

Since this is a local mock, you must tell your AWS clients (CLI, Boto3, JS SDK) to use the local endpoint.

Note: You must specify a region and fake credentials.

### AWS CLI
#### 1. Configure fake credentials for the session
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=eu-central-1

#### 2. Run commands pointing to localhost
    aws --endpoint-url=http://localhost:4566 cognito-idp create-user-pool --pool-name "MyPersistentPool"

### Python (Boto3)
    import boto3

    cognito = boto3.client(
        "cognito-idp",
        region_name="eu-central-1",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )
    cognito.create_user_pool(PoolName="MyTestPool")

### JavaScript / TypeScript (AWS SDK v3)
    import { CognitoIdentityProviderClient } from "@aws-sdk/client-cognito-identity-provider";

    const client = new CognitoIdentityProviderClient({
      region: "eu-central-1",
      endpoint: "http://localhost:4566",
      credentials: {
        accessKeyId: "test",
        secretAccessKey: "test",
      },
    });

## ⚙️ Configuration

You can configure the behavior using Environment Variables in Docker:

|   Variable    | Default          | Description                                    |
|---------------|------------------|------------------------------------------------|
|     PORT      | 4566             | The port the server listens on.                |
|   DATA_FILE   | /data/cognito.db | Path inside the container where data is saved. |
| SAVE_INTERVAL | 60               | How often (in seconds) to auto-save to disk.   |

## 🧪 Development

If you want to contribute or run this locally without Docker:

### 1. Clone repo
    git clone https://github.com/m-ali-ubit/cognitoidp-local.git
    cd cognitoidp-local

### 2. Install dependencies
pip install -e .[dev]

### 3. Run Server
python -m cognitoidp_local.main

### 4. Run Tests
pytest


## ⚖️ License

Apache License 2.0

This project is not affiliated with AWS or LocalStack. It is an independent open-source tool based on the Moto library.
