#!C:\Program Files\Git\bin\bash.exe
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE ${POSTGRES_USERS_TB} (
        user_id UUID PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
        last_login TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
        storage_used BIGINT NOT NULL DEFAULT 0,
        storage_quota BIGINT NOT NULL DEFAULT 10737418240
    );
    
    CREATE TABLE ${POSTGRES_META_TB} (
        object_id UUID PRIMARY KEY,
        user_id UUID,
        bucket TEXT NOT NULL,
        folder VARCHAR(255),
        object_key TEXT NOT NULL,
        original_name TEXT NOT NULL,
        current_name TEXT NOT NULL,
        content_type VARCHAR(255),
        size_bytes BIGINT NOT NULL,
        sha256_hex VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'),
        CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES ${POSTGRES_USERS_TB}(user_id) ON DELETE CASCADE
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

    GRANT USAGE ON SCHEMA public TO ${APP_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${APP_USER};
EOSQL