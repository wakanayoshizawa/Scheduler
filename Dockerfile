FROM python:3.8

ADD ./ /bot
WORKDIR /bot

RUN apt-get -y update && apt-get install -y libzbar-dev
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
