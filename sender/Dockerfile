FROM python:3.9-slim
WORKDIR /app
COPY sender.py .
# Folder results tetap di-mount agar data bisa keluar
CMD ["python", "-u", "sender.py"]
