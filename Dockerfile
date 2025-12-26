FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY cognitoidp_local/ ./cognitoidp_local/
RUN pip install --no-cache-dir .

RUN mkdir /data
VOLUME /data

ENV PYTHONUNBUFFERED=1
ENV PORT=4566
ENV DATA_FILE=/data/cognito.db

EXPOSE 4566

CMD ["cognitoidp-local"]
