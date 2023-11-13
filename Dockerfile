FROM python:3.8
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY exporter.py /opt
WORKDIR /opt
EXPOSE 8000
EXPOSE 9000
CMD ["python3","exporter.py"]

#docker build --no-cache -t "xag/conformance_monitor
#docker run -d --name conformance_monitor -p 8000:8000 xag/conformance_monitor