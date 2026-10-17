FROM python:3.12-slim
RUN groupadd --gid 10001 lab && useradd --uid 10001 --gid lab --no-create-home lab
WORKDIR /app
COPY server.py .
USER 10001:10001
EXPOSE 8000
CMD ["python", "-u", "server.py"]
