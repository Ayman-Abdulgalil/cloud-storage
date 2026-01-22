#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    CREATE TABLE ${POSTGRES_META_TB} (
        object_id UUID PRIMARY KEY,
        user_id TEXT,
        bucket TEXT NOT NULL,
        folder VARCHAR(255),
        object_key TEXT NOT NULL,
        original_name TEXT NOT NULL,
        current_name TEXT NOT NULL,
        content_type VARCHAR(255),
        size_bytes BIGINT NOT NULL,
        sha256_hex VARCHAR(64) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
    );

    CREATE TABLE ${POSTGRES_USERS_TB} (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP WITH TIME ZONE,
        is_active BOOLEAN DEFAULT TRUE,
        storage_used BIGINT DEFAULT 0,
        storage_quota BIGINT DEFAULT 10737418240,
    );

    CREATE INDEX idx_${POSTGRES_USERS_TB}_email ON ${POSTGRES_USERS_TB}(email);
    CREATE INDEX idx_${POSTGRES_USERS_TB}_created_at ON ${POSTGRES_USERS_TB}(created_at);
    CREATE INDEX idx_${POSTGRES_META_TB}_folder ON ${POSTGRES_META_TB}(folder);
    CREATE INDEX idx_${POSTGRES_META_TB}_user_id ON ${POSTGRES_META_TB}(user_id);
    CREATE INDEX idx_${POSTGRES_META_TB}_created_at ON ${POSTGRES_META_TB}(created_at);
    CREATE INDEX idx_${POSTGRES_META_TB}_sha256 ON ${POSTGRES_META_TB}(sha256_hex);

    CREATE USER ${APP_USER} WITH PASSWORD '${APP_USER_PASSWORD}';
    
    GRANT ALL PRIVILEGES ON TABLE ${POSTGRES_USERS_TB} TO ${APP_USER};
    GRANT ALL PRIVILEGES ON TABLE ${POSTGRES_META_TB} TO ${APP_USER};
    
    GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO ${APP_USER};
EOSQL