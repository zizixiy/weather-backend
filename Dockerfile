FROM python:3.13-slim

WORKDIR /app

ENV PIP_INDEX_URL=https://mirrors.ustc.edu.cn/pypi/simple

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT:-32020}

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-32020}
