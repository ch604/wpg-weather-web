FROM python:3.12-slim
ADD wpg-weather-web.py .
RUN pip install NOAA pygame feedparser noaa_sdk
CMD ["python", "./wpg-weather-web.py"]