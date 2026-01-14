-- ============================================================
-- Turkcell Decision Engine - PostgreSQL Database Schema
-- Code Night 2026
-- ============================================================

-- Veritabanı oluşturma (pgAdmin'de manuel veya bu komutla)
-- CREATE DATABASE turkcell_decision_engine;

-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

-- Risk seviyesi enum
CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

-- Servis türleri enum
CREATE TYPE service_enum AS ENUM ('Superonline', 'Paycell', 'TV+', 'Fizy', 'Game+', 'BiP');

-- Event türleri enum
CREATE TYPE event_type_enum AS ENUM ('USAGE', 'PAYMENT', 'CONTENT_CONSUMPTION');

-- Aksiyon türleri enum
CREATE TYPE action_type_enum AS ENUM (
    'DATA_USAGE_WARNING',
    'SPEND_ALERT', 
    'CONTENT_COOLDOWN_SUGGESTION',
    'CRITICAL_ALERT',
    'DATA_USAGE_NUDGE',
    'SPEND_NUDGE'
);

-- Birim türleri enum
CREATE TYPE unit_enum AS ENUM ('GB', 'TRY', 'MIN');

-- ============================================================
-- 2. TABLES
-- ============================================================

-- Kullanıcılar tablosu
CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'Turkcell kullanıcıları';

-- ============================================================

-- Eventler tablosu
CREATE TABLE events (
    event_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    service service_enum NOT NULL,
    event_type event_type_enum NOT NULL,
    value DECIMAL(10, 2) NOT NULL CHECK (value >= 0),
    unit unit_enum NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE events IS 'Servislerden gelen tüm eventler';

CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_processed ON events(processed);

-- ============================================================

-- Kullanıcı durumu tablosu
CREATE TABLE user_state (
    user_id VARCHAR(10) PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    internet_today_gb DECIMAL(10, 2) DEFAULT 0.0 CHECK (internet_today_gb >= 0),
    spend_today_try DECIMAL(10, 2) DEFAULT 0.0 CHECK (spend_today_try >= 0),
    content_minutes_today DECIMAL(10, 2) DEFAULT 0.0 CHECK (content_minutes_today >= 0),
    risk_level risk_level_enum DEFAULT 'LOW',
    state_date DATE DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_state IS 'Kullanıcıların günlük durumu';

CREATE INDEX idx_user_state_risk ON user_state(risk_level);
CREATE INDEX idx_user_state_date ON user_state(state_date);

-- ============================================================

-- Kurallar tablosu
CREATE TABLE rules (
    rule_id VARCHAR(10) PRIMARY KEY,
    condition TEXT NOT NULL,
    action action_type_enum NOT NULL,
    priority INTEGER NOT NULL CHECK (priority >= 1),
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE rules IS 'Karar motoru kuralları - kod içine gömülmeden veri olarak saklanır';

CREATE INDEX idx_rules_active ON rules(is_active);
CREATE INDEX idx_rules_priority ON rules(priority);

-- ============================================================

-- Aksiyonlar tablosu
CREATE TABLE actions (
    action_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action_type action_type_enum NOT NULL,
    message TEXT,
    sent_via VARCHAR(20) DEFAULT 'BiP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE actions IS 'Kullanıcılara gönderilen aksiyonlar/bildirimler';

CREATE INDEX idx_actions_user_id ON actions(user_id);
CREATE INDEX idx_actions_type ON actions(action_type);
CREATE INDEX idx_actions_created ON actions(created_at);

-- ============================================================

-- Kararlar tablosu (Audit Log)
CREATE TABLE decisions (
    decision_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    triggered_rules TEXT[] NOT NULL,  -- Array of rule_ids
    selected_action action_type_enum NOT NULL,
    suppressed_actions action_type_enum[],  -- Array of suppressed actions
    user_state_snapshot JSONB,  -- Karar anındaki kullanıcı durumu
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE decisions IS 'Tüm kararların audit log kaydı';

CREATE INDEX idx_decisions_user_id ON decisions(user_id);
CREATE INDEX idx_decisions_timestamp ON decisions(timestamp);
CREATE INDEX idx_decisions_selected ON decisions(selected_action);

-- ============================================================
-- 3. VIEWS (Dashboard için)
-- ============================================================

-- Günlük özet view
CREATE VIEW v_daily_summary AS
SELECT 
    COUNT(DISTINCT e.user_id) AS active_users,
    COUNT(e.event_id) AS total_events,
    COUNT(a.action_id) AS total_actions,
    COUNT(d.decision_id) AS total_decisions,
    CURRENT_DATE AS summary_date
FROM events e
LEFT JOIN actions a ON DATE(a.created_at) = CURRENT_DATE
LEFT JOIN decisions d ON DATE(d.timestamp) = CURRENT_DATE
WHERE DATE(e.timestamp) = CURRENT_DATE;

-- Risk bazlı kullanıcı özeti
CREATE VIEW v_users_by_risk AS
SELECT 
    risk_level,
    COUNT(*) AS user_count
FROM user_state
GROUP BY risk_level
ORDER BY 
    CASE risk_level 
        WHEN 'CRITICAL' THEN 1 
        WHEN 'HIGH' THEN 2 
        WHEN 'MEDIUM' THEN 3 
        WHEN 'LOW' THEN 4 
    END;

-- Son aksiyonlar view
CREATE VIEW v_recent_actions AS
SELECT 
    a.action_id,
    a.user_id,
    u.name AS user_name,
    a.action_type,
    a.message,
    a.created_at
FROM actions a
JOIN users u ON a.user_id = u.user_id
ORDER BY a.created_at DESC
LIMIT 50;

-- ============================================================
-- 4. FUNCTIONS
-- ============================================================

-- Risk seviyesi hesaplama fonksiyonu
CREATE OR REPLACE FUNCTION calculate_risk_level(
    p_internet_gb DECIMAL,
    p_spend_try DECIMAL,
    p_content_min DECIMAL
) RETURNS risk_level_enum AS $$
BEGIN
    -- CRITICAL: Hem internet hem harcama yüksek
    IF p_internet_gb > 15 AND p_spend_try > 300 THEN
        RETURN 'CRITICAL';
    -- HIGH: Herhangi biri yüksek
    ELSIF p_internet_gb > 15 OR p_spend_try > 300 OR p_content_min > 240 THEN
        RETURN 'HIGH';
    -- MEDIUM: Orta seviye
    ELSIF p_internet_gb > 10 OR p_spend_try > 200 OR p_content_min > 120 THEN
        RETURN 'MEDIUM';
    -- LOW: Normal kullanım
    ELSE
        RETURN 'LOW';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- User state güncelleme fonksiyonu
CREATE OR REPLACE FUNCTION update_user_state_from_event()
RETURNS TRIGGER AS $$
BEGIN
    -- User state yoksa oluştur
    INSERT INTO user_state (user_id, state_date)
    VALUES (NEW.user_id, CURRENT_DATE)
    ON CONFLICT (user_id) DO NOTHING;
    
    -- Event tipine göre state güncelle
    IF NEW.unit = 'GB' THEN
        UPDATE user_state 
        SET internet_today_gb = internet_today_gb + NEW.value,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id;
    ELSIF NEW.unit = 'TRY' THEN
        UPDATE user_state 
        SET spend_today_try = spend_today_try + NEW.value,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id;
    ELSIF NEW.unit = 'MIN' THEN
        UPDATE user_state 
        SET content_minutes_today = content_minutes_today + NEW.value,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = NEW.user_id;
    END IF;
    
    -- Risk seviyesini güncelle
    UPDATE user_state 
    SET risk_level = calculate_risk_level(
        internet_today_gb, 
        spend_today_try, 
        content_minutes_today
    )
    WHERE user_id = NEW.user_id;
    
    -- Event'i işlenmiş olarak işaretle
    NEW.processed = TRUE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 5. TRIGGERS
-- ============================================================

-- Event eklendiğinde user state'i otomatik güncelle
CREATE TRIGGER trg_update_user_state
    BEFORE INSERT ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_user_state_from_event();

-- Updated_at otomatik güncelleme
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_rules_updated
    BEFORE UPDATE ON rules
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================================
-- 6. SEQUENCES (ID generation için)
-- ============================================================

CREATE SEQUENCE event_id_seq START 1001;
CREATE SEQUENCE action_id_seq START 1000;
CREATE SEQUENCE decision_id_seq START 900;

-- ============================================================
-- Şema oluşturma tamamlandı!
-- pgAdmin4'te bu dosyayı Query Tool ile çalıştırabilirsiniz.
-- ============================================================
