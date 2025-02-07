# 🐍 Utiliser une image Python légère
FROM python:3.8-slim

# 📂 Définir le répertoire de travail
WORKDIR /app

# 🏗️ Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y ffmpeg

# 📜 Copier les fichiers du bot dans le conteneur
COPY . /app

# 🔧 Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 Lancer le bot Telegram
CMD ["python", "réseau social.py"]
