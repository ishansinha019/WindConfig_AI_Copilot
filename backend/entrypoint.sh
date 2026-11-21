#!/bin/sh
set -eu

alembic upgrade head
python -m app.db.seed
exec fastapi run app/main.py --host 0.0.0.0 --port 8000
