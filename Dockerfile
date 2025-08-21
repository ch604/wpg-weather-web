FROM python:3.12-slim
ADD wpg-weather-web.py .
add requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "./wpg-weather-web.py"]