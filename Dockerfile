FROM python:3.10
WORKDIR /app
COPY requirements.txt /app
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r /app/requirements.txt
COPY . /app
EXPOSE 8000
ENV PYTHONPATH=/app
CMD ["python", "main.py"]
HEALTHCHECK --timeout=5s CMD curl -f http://localhost:12345/ || exit 1