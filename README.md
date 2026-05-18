# Network Validation Tests

This project uses Python and Behave to validate basic network connectivity requirements.

## What It Tests

- Retrieves the machine's public IP address from `https://ipinfo.io/ip`.
- Verifies that the public IP is not in the restricted range `101.33.28.0 - 101.33.29.0`.
- Resolves `google-public-dns-a.google.com` and checks that it resolves to `8.8.8.8`.
- Runs a traceroute to `8.8.8.8` and verifies that the target is reached within 10 hops.

## Requirements

- Python 3.12 or compatible Python 3 version
- `tracert` on Windows or `traceroute` on Linux/macOS

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
behave
```

On Windows, if the console has encoding issues, run:

```powershell
$env:PYTHONIOENCODING='utf-8'
behave
```

## Run With Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

Or build and run directly:

```bash
docker build -t network-tests .
docker run --rm --network host network-tests
```

## Project Structure

```text
features/
  network.feature
  environment.py
  steps/
    network_steps.py
behave.ini
requirements.txt
Dockerfile
docker-compose.yml
```
