FROM python:3.6

ADD requirements.txt /root/requirements.txt
ADD app /root/app
ENV PYTHONPATH=/root/app
WORKDIR /root/app

RUN pip install -r ../requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
