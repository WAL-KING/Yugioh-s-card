# Utilisation d'une image Python légère
FROM python:3.10

# Définition du répertoire de travail
WORKDIR /app

# Copier tous les fichiers dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lancer le bot
CMD ["python", "monbot.py"]
