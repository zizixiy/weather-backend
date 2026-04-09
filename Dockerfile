FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -i https://mirrors.ustc.edu.cn/pypi/simple uv
RUN uv sync

EXPOSE ${PORT:-32020}

CMD uv run uvicorn app:app --host 0.0.0.0 --port ${PORT:-32020}
