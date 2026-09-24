FROM python:3.12-alpine
WORKDIR /app
COPY app.py /app/app.py
RUN addgroup -S ctf && adduser -S ctf -G ctf
USER ctf
EXPOSE 8080
CMD ["python", "app.py"]
