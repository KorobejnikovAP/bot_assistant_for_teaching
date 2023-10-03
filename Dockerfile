FROM python:3.10

WORKDIR /usr/src/app/

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
 
COPY . .

