# Usa una imagen base adecuada
FROM python:3.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos de la aplicación al contenedor
COPY . .

# Instala las dependencias de tu aplicación
RUN pip3 install -r requirements.txt

# Expone el puerto en el que se ejecuta tu aplicación
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
