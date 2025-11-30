# Basis-Image mit Python
FROM python:3.13

# Arbeitsverzeichnis im Container
WORKDIR /app

# Installiert dependencies aus requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert restlichen Code aus /cryptosim
COPY . .

# Flask bzw. Port festlegen
EXPOSE 5000

# Starten des Containers / Mit RUN allein würde es nicht den Container starten
CMD ["python", "app.py"]


