<h3 align="center">Article Tracker</h3>

<div align="center">
  <img src="https://img.shields.io/badge/status-active-success.svg" />
  <img src="https://img.shields.io/badge/python-3.13-blue" />
</div>

---

<p align="center">article-tracker
    <br> 
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
- [Built Using](#built-using)

## 🧐 About <a name = "about"></a>
**Article Tracker** is a system designed to crawl the articles from [Tageschau](https://www.tagesschau.de/). And it consists of:
- A web crawler that periodically fetches the articles content.
- A PostgreSQL database to store articles and maintain version history.
- Two Flask APIs:
    - Controller API – Manages the crawler (triggering crawls, adjusting frequency, etc.).
    - Explorer API – Allows listing, searching and tracking changes in articles over time.

Features
- Periodic and on-demand article crawling.
- Version tracking for content updates.
- Search functionality.
- API-based control over crawling behavior.


### Database Schema
<div style="text-align: center;">
  <img src="images/schema.png" alt="Diagram" width="600" />
</div>

## 🏁 Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites
 - [Docker](https://docs.docker.com/)
 - [Docker Compose](https://docs.docker.com/compose/)

### Installing
If you're opening this project using [devcontainers](https://containers.dev/) then your docker container should be ready to go!

Otherwise you will need to start the docker compose environment `docker compose up` and open a shell into the container `article-tracker-dev`.

```bash
$ docker compose up
$ docker exec -it article-tracker-dev /bin/bash   # spawns a shell within the docker container
$ pipenv shell  # spawns a shell within the virtualenv 
```

### ▶️ Running the API
```bash
$ python run.py
```

Endpoints:
- [API Docs](http://localhost:5555/openapi/swagger)
- [Healthcheck](http://localhost:5555/health)


### Database Migrations

```bash
# init the migrations folder
$ alembic init migrations  

# create a new migration version
$ alembic revision --autogenerate -m "message"  

# apply migrations
$ alembic upgrade head
```

*Note: If you're setting up this project, you only need to apply the existing migrations, as they have already been generated.*

### 🧪 Running the tests <a name = "tests"></a>
- [pytest](https://docs.pytest.org/) is used to run unit and integration tests.   

🚧 Work in Progress

### Code Style & Linting
The following tools are run during pipelines to enforce code style and quality.

 - [flake8](https://flake8.pycqa.org/en/latest/) for linting
 - [isort](https://pycqa.github.io/isort/) for import sorting
 - [black](https://black.readthedocs.io/en/stable/) for code style

### Python Package Management
- [pipenv](https://pipenv.pypa.io/en/latest/) is used to manage Python packages. 

```bash
$ pipenv shell  # spawns a shell within the virtualenv
$ pipenv install  # installs all packages from Pipfile
$ pipenv install --dev # installs all packages from Pipfile, including dev dependencies
$ pipenv install <package1> <package2>  # installs provided packages and adds them to Pipfile
$ pipenv update  # update package versions in Pipfile.lock, this should be run frequently to keep packages up to date
$ pipenv uninstall package # uninstall a package 
$ pipenv uninstall package  --categories dev-packages # uninstall a dev package
```

## ⛏️ Built Using <a name = "built_using"></a>
- [Flask](https://flask.palletsprojects.com/en/stable/) - Web Framework.
- [flask-openapi3](https://luolingchun.github.io/flask-openapi3/v4.x/) - API Documentation
- [PostgreSQL](https://www.postgresql.org/) - Database.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database Migration.
- [Requests-HTML](https://requests.readthedocs.io/projects/requests-html/en/latest/) - For web scraping and HTML parsing
- [APScheduler](https://apscheduler.readthedocs.io/) - Python Scheduler