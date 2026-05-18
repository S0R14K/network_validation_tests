FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
LABEL maintainer="candidate"
LABEL description="Network validation tests using Behave (Python Cucumber)"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends traceroute && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY . .
ENTRYPOINT ["behave"]
CMD ["--no-capture", "--format", "pretty"]
