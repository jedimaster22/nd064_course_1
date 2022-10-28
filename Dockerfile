FROM python:3.8

EXPOSE 3111

LABEL maintainer="Wyndell Lowie"

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN python3 init_db.py

CMD ["python3", "app.py"]
