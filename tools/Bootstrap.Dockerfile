FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
COPY requirements.lock /bootstrap/requirements.lock
COPY tools/coverage-requirements.txt /bootstrap/coverage-requirements.txt
RUN pip install --no-cache-dir -r /bootstrap/requirements.lock -r /bootstrap/coverage-requirements.txt
WORKDIR /src
ENV SKIP_INTEGRATION=0 PYTHONPATH=/src PYTHONDONTWRITEBYTECODE=1
