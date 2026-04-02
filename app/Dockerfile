FROM python:3.10.20-alpine3.22

LABEL maintainer="Esteban Heschung <esteban.heschung@etudiant.univ-rennes.fr>"
LABEL description="Microservice Flask pour gérer les evenements" 
LABEL service="events_service"

RUN apk add --no-cache curl # curl pour healthcheck

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/app.py .

EXPOSE 5004

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:5004/events/health || exit 1

CMD ["python", "app.py"]
