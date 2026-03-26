FROM python:3.11.15-trixie

LABEL maintainer="Esteban Heschung <esteban.heschung@etudiant.univ-rennes.fr>"
LABEL description="Microservice Flask pour gérer les evenements" 
LABEL service="events_service"

RUN apt-get update && apt-get upgrade -y && apt-get install -y curl && apt-get clean #curl pour healthcheck

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5004

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:5004/events || exit 1

CMD ["python", "app.py"]
