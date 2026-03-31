# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.0] - 31/03/2026
### Added
- Création du service **Events** en Flask.
- Gestion des événements liés aux déploiements :
  - Liste de tous les événements (`/events` - GET)
  - Liste des événements d’un déploiement spécifique (`/deployments/<deployment_id>/events` - GET)
  - Création d’un événement (`/events` - POST)
  - Récupération d’un événement par son ID (`/events/<event_id>` - GET)
- Validation des champs obligatoires : `deploymentId`, `type`, `message`.
- Vérification de l’existence des IDs pour `deploymentId` et `initiatedBy` via les services **Deployments** et **Users**.
- Types d’événements supportés : `DEPLOYMENT_STARTED`, `DEPLOYMENT_FINISHED`, `DEPLOYMENT_ERROR`, `ROLLBACK`.
- Stockage persistant des événements dans `data.json`.
- Authentification et vérification des tokens via le service `/auth/verify`.
- Endpoint **health** pour le service Events (`/events/health`).
- Gestion des erreurs : service injoignable, ID inexistant, champ manquant, type invalide.

### Changed
- N/A (première version)

### Fixed
- N/A (première version)