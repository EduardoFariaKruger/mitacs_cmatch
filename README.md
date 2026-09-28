# CMATCH

LLM-assisted multi-objective resource selection for Sky Computing.

## Requirements

* Python 3.10+
* Docker
* Docker Compose
* Make
* dump.sql file
* OpenRouter API Key

## Project Structure

```text
.
├── cmatch/
│   ├── __init__.py
│   ├── llm_interactions.py
│   ├── main.py
│   ├── utils.py
│   └── __pycache__/
├── docker-compose.yaml
├── Makefile
├── pyproject.toml
└── README.md
```

### Python Package

The `cmatch/` directory contains the CMATCH Python package.

* `main.py` - Main application and CLI entry point.
* `llm_interactions.py` - LLM interaction and constraint extraction.
* `utils.py` - Utility functions used by CMATCH.

## Installation

Clone the repository:

```
git clone https://github.com/EduardoFariaKruger/mitacs_cmatch.git
cd mitacs_cmatch
```

Create a virtual environment:

```
python3 -m venv venv
```

Activate the virtual environment:

```
source venv/bin/activate
```

Create the environment file and fill with your open router Keys:

```
cp .env.example .env
```

Install CMATCH:

```
make install
```

## Database

CMATCH uses PostgreSQL with PostGIS.

Start PostgreSQL:

```
make db-up
```

Initialize the database and import `dump.sql`:

```
make db-init
```

The database is available at:

```
localhost:5432
```

Default credentials:

```
Database: postgres
User: postgres
Password: 123mudar
```

## Run

Run CMATCH:

```
make run
```

Or directly:

```
cmatch
```

## Make Commands

### Install

Install CMATCH:

```
make install
```

### Install for development

Install CMATCH in editable mode:

```
make install-dev
```

### Install globally

Make `cmatch` available from any path:

```
make install-global
```

### Start database

Start PostgreSQL:

```
make db-up
```

### Initialize database

Start PostgreSQL and import `dump.sql`:

```
make db-init
```

### Stop database

Stop PostgreSQL:

```
make db-down
```

### Reset database

Remove PostgreSQL and all stored data:

```
make db-reset
```

### Run

Run CMATCH:

```
make run
```

### Clean

Remove build and temporary files:

```
make clean
```

## Quick Start

For a new installation:

```
python3 -m venv venv
source venv/bin/activate
cp .env.example .env
make install
make db-init
make run
```
