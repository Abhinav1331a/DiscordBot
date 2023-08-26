FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HOST=0.0.0.0
ENV PORT=80
EXPOSE 80

CMD [ "python", "main.py", "--host", "0.0.0.0", "--port", "80" ]
