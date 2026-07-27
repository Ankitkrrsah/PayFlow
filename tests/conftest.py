import pytest
import os
from fastapi.testclient import TestClient
import psycopg2
from app.main import app
from app.db.pool import get_conn, redis_client

# Set a test environment variable so pool.py can use a test DB if needed, or just use the current one.
# For simplicity, we'll truncate tables on the current DB since it's a test environment.

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def truncate_tables():
    """Truncate tables before each test to ensure a clean state."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # We don't truncate schema_migrations
            cur.execute("""
                TRUNCATE TABLE 
                users, merchants, payment_links, transactions, refunds, webhooks, webhook_logs 
                RESTART IDENTITY CASCADE;
            """)
        conn.commit()
    finally:
        # Assuming release_conn exists or we just close
        # From code: from app.db.pool import get_conn, release_conn
        from app.db.pool import release_conn
        release_conn(conn)
        
    if redis_client:
        redis_client.flushdb()
