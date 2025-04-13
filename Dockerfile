FROM python:3.13.0-slim

WORKDIR /app
COPY .. .

RUN pip install --root-user-action=ignore --upgrade pip && pip install --root-user-action=ignore -r requirements.txt && rm -rf ~/.cache/pip

CMD python3 run.py run