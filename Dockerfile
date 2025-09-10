FROM python:3.12-slim AS build

RUN mkdir ./templates ./static

COPY ["wpg-weather-web.py", "county_adjacency_by_fips.json", "requirements.txt", "./"]
COPY templates/ ./templates/
COPY static/ ./templates/

RUN pip install -r requirements.txt

CMD ["python", "./wpg-weather-web.py"]