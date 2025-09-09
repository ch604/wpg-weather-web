FROM python:3.12-slim

ADD wpg-weather-web.py .
ADD templates .
ADD static .
ADD county_adjacency_by_fips.json
ADD requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "./wpg-weather-web.py"]