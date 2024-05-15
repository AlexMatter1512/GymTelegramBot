FROM python:alpine

COPY requirements.txt /bot/requirements.txt
RUN pip install -r /bot/requirements.txt

COPY bot.py /bot/bot.py
COPY module/ /bot/module/
COPY config.yaml /bot/config.yaml


CMD ["python", "/bot/bot.py"]