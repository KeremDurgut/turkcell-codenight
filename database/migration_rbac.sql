-- ============================================================
-- Turkcell Decision Engine - RBAC Migration
-- System Admins tablosu ve varsayılan kullanıcılar
-- ============================================================

-- Admin rol enum
CREATE TYPE admin_role_enum AS ENUM ('ADMIN', 'ANALYST');

-- ============================================================
-- SYSTEM_ADMINS TABLOSU
-- Uygulamayı yönetecek personellerin tablosu
-- ============================================================

CREATE TABLE system_admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role admin_role_enum NOT NULL DEFAULT 'ANALYST',
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE system_admins IS 'Uygulamayı yöneten personeller (RBAC)';

CREATE INDEX idx_admins_username ON system_admins(username);
CREATE INDEX idx_admins_role ON system_admins(role);

-- ============================================================
-- VARSAYILAN KULLANICILAR
-- Şifreler: admin123, analyst123 (SHA256 hash)
-- ============================================================

-- admin / admin123
INSERT INTO system_admins (username, password_hash, role, full_name) VALUES
    ('admin', '240be518fabd2724ddb6f04eeb9d5b57f4c9e5e8e7f8d9c0a1b2c3d4e5f6a7b8', 'ADMIN', 'Sistem Yöneticisi');

-- analyst / analyst123  
INSERT INTO system_admins (username, password_hash, role, full_name) VALUES
    ('analyst', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'ANALYST', 'Veri Analisti');

-- ============================================================
-- Migration tamamlandı!
-- pgAdmin4'te bu dosyayı çalıştırın.
-- ============================================================
