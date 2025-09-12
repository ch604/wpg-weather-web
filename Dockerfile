FROM python:3.12-slim AS build

RUN mkdir ./templates ./static

COPY ["wpg-weather-web.py", "county_adjacency_by_fips.json", "requirements.txt", "./"]
COPY templates/ ./templates/
COPY static/ ./static/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "--access-logfile", "-", "wpg-weather-web:app"]