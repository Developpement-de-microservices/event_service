# Events Service – SAE401

Microservice de gestion des événements liés aux déploiements dans la plateforme de gestion des déploiements d’applications.

---

## Description

Le service **Events** permet de tracer et consulter tous les événements liés aux déploiements.

Il sert principalement à :

* Suivre le cycle de vie d’un déploiement
* Enregistrer les actions (début, fin, erreur, rollback…)
* Fournir un historique pour le debug et l’audit

---

## Fonctionnalités

* Création d’un événement
* Consultation d’un événement
* Liste des événements avec pagination
* Filtrage par :
  * deploymentId
  * type
  * initiatedBy
* Consultation des événements d’un déploiement spécifique

---

## Modèle de données

### Event

```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "deploymentId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "type": "DEPLOYMENT_STARTED",
      "message": "Working",
      "data": {
        "additionalProp1": {}
      },
      "initiatedBy": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "createdAt": "2026-03-25T12:30:04.763Z"
    }
```

### Champs

| Champ        | Description                        |
| ------------ | ---------------------------------- |
| id           | Identifiant unique (UUID)          |
| deploymentId | ID du déploiement lié              |
| type         | Type d’événement                   |
| message      | Description lisible                |
| data         | Données supplémentaires (flexible) |
| initiatedBy  | ID de l’utilisateur ou service     |
| createdAt    | Date de création                   |

---

## Types d’événements

Exemples :

* `DEPLOYMENT_STARTED`
* `DEPLOYMENT_FINISHED`
* `DEPLOYMENT_FAILED`
* `ROLLBACK_STARTED`
* `ROLLBACK_COMPLETED`

---

## Architecture

* Microservice indépendant
* Communication via REST / JSON
* Intégré avec :

  * /deployments (source principale des événements)
  * /users

---

## Remarques

* Le champ `data` est volontairement flexible pour s’adapter à chaque type d’événement
* Les identifiants sont générés en UUID
* Ce service est conçu pour être utilisé avec un proxy dans l’architecture globale

---
