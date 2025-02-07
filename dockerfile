FROM  python:3.12.3

#goes to the app directory
WORKDIR /app

#copy requirments.txt which is a list of dependencies
COPY requirments.txt .

#pip install dependencies
RUN pip install --no-cache-dir -r requirments.txt

#copy ffmpeg and set it as executable
RUN apt-get update && apt-get install -y ffmpeg

COPY . .

CMD ["python", "main.py"]