

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

COPY my_api /app/
#COPY my_api/requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

