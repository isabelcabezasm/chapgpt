FROM python:3.12.8-bullseye
#torchvision needs python >=3.8, <=3.12

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY *.py .

COPY yolo5_finetunned yolo5_finetunned

RUN apt-get update && apt-get install -y libgl1

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]