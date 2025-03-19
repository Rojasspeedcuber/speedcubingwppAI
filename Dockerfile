FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor a porta que será usada pela API
EXPOSE 8000

# Variáveis de ambiente para Flask
ENV FLASK_APP=app/main.py
ENV FLASK_ENV=production

# Comando para iniciar a aplicação
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"] 