FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
WORKDIR /app
COPY selector.py scheduler.py impact.py line_impact.py /app/
COPY maps/base-map.json.gz maps/return-sites.json.gz /app/maps/
CMD ["python", "/app/selector.py"]
