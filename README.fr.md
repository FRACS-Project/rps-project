# RPS : Recipe · Planning · Shopping

[English](README.md) · **Français**

RPS est le backend d'une application de cuisine. Les utilisateurs y gèrent leurs recettes, planifient leurs repas et préparent leurs listes de courses. À terme, l'objectif est d'en faire un petit réseau social autour de la cuisine.

> **Statut : alpha, en développement actif.** Les recettes et l'authentification fonctionnent. Le planning, les courses et le garde-manger (« fridge ») sont prévus dans la roadmap.

## Stack technique

| Domaine | Outils |
|---|---|
| API | Python 3.12, FastAPI, Pydantic |
| Données | SQLModel (SQLAlchemy), PostgreSQL 15 |
| Authentification | OAuth2 password flow, JWT (python-jose), bcrypt (passlib) |
| Infra | Docker, Docker Compose, reverse proxy Nginx |
| Outillage | uv, pytest |

Le client mobile Flutter est développé à part et ne fait pas partie de ce dépôt.

## Fonctionnalités

- **Authentification** : inscription, puis connexion par nom d'utilisateur ou par e-mail (formulaire OAuth2 ou JSON). Les requêtes sont authentifiées par un jeton JWT de type bearer.
- **Utilisateurs** : un compte peut être marqué administrateur ou désactivé. Seuls les administrateurs gèrent les utilisateurs.
- **Recettes** : CRUD complet, avec ingrédients, étapes ordonnées, tags et images.
- **Favoris** : chaque utilisateur peut enregistrer des recettes dans sa propre liste.
- **Propriété des données** : les routes `/me` ne lisent et ne modifient que les ressources de l'utilisateur connecté.
- **Catalogue partagé** : ingrédients et tags, modifiables uniquement par les administrateurs.

### Choix de sécurité

- Les mots de passe sont hachés avec bcrypt. Ils doivent faire au moins 12 caractères et contenir une majuscule, une minuscule, un chiffre et un caractère spécial.
- Les noms d'utilisateur sont validés et les adresses e-mail normalisées.
- Pour les images envoyées, le type MIME réel est vérifié avec python-magic, et non l'extension du fichier. Nginx limite la taille des requêtes à 10 Mo.
- Le conteneur de l'API tourne avec un utilisateur non-root. Il n'est jamais exposé directement sur l'hôte : on y accède seulement via Nginx.
- Tous les secrets passent par des variables d'environnement. Aucun n'est versionné.

## Architecture

Le code est organisé par domaine, et chaque domaine suit les mêmes couches :

```
routers  →  services  →  crud  →  models
(HTTP)      (règles)      (BDD)   (tables SQLModel)
```

Chaque domaine a aussi ses `schemas` (modèles d'entrée et de sortie) et ses propres `exceptions`.

```
apps/api/
├── auth/            # connexion, inscription, JWT
├── user/
├── recipe/
│   └── components/  # instruction, recipe_ingredient, recipe_tag
├── shared/          # ingredient, tag, image, bookmark
├── planning/        # roadmap
├── shopping/        # roadmap
├── core/            # config, sécurité, chemins
├── db/              # engine et session
└── main.py
docker/              # config nginx, entrypoint du conteneur
tests/
```

## Démarrage

### Avec Docker (recommandé)

```bash
cp .env.example .env
# dans .env, renseigner SECRET_KEY (openssl rand -hex 32) et POSTGRES_PASSWORD
docker compose up --build
```

L'API est servie par Nginx sur **http://localhost:8080**. La documentation interactive se trouve sur **http://localhost:8080/docs**.

La stack comprend trois services : `db` (PostgreSQL), `backend` (FastAPI/uvicorn) et `nginx`. Les tables sont créées automatiquement au démarrage.

### Lancer les tests

```bash
uv sync
uv run pytest
```

Les tests utilisent une base SQLite en mémoire. Ils n'ont besoin ni de Docker ni de PostgreSQL.

## Aperçu de l'API

| Préfixe | Rôle |
|---|---|
| `/auth` | `signup`, `login`, `login-json`, `me` |
| `/users` | gestion des utilisateurs (admin) |
| `/recipe` | recettes ; `/recipe/me` pour celles de l'utilisateur connecté |
| `/recipe_ingredient`, `/instruction` | composants d'une recette |
| `/ingredient`, `/tag` | catalogue partagé |
| `/bookmark/me` | recettes en favoris |
| `/image` | images des recettes |

Le schéma complet et à jour est disponible sur `/docs`.

## Roadmap

- [ ] Modules Planning, Shopping et Fridge
- [ ] HTTPS sur Nginx
- [ ] Suite de tests plus complète (tests d'intégration, meilleure couverture)
- [ ] Déploiement auto-hébergé sur un serveur Linux personnel, avec accès à distance via Tailscale
