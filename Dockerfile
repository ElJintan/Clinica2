FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para ejecutar la app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]