FROM python:3

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "spotico.py", "-c", "-i 60" ]

