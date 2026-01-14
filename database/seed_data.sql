-- ============================================================
-- Turkcell Decision Engine - Seed Data
-- CSV dosyalarından alınan örnek veriler
-- ============================================================

-- ============================================================
-- 1. USERS
-- ============================================================
INSERT INTO users (user_id, name, city) VALUES
    ('U1', 'Ayşe', 'Istanbul'),
    ('U2', 'Ali', 'Ankara'),
    ('U3', 'Deniz', 'Izmir'),
    ('U4', 'Mert', 'Bursa'),
    ('U5', 'Ece', 'Antalya');

-- ============================================================
-- 2. RULES (Kurallar)
-- ============================================================
INSERT INTO rules (rule_id, condition, action, priority, is_active, description) VALUES
    ('R-01', 'internet_today_gb > 15', 'DATA_USAGE_WARNING', 3, TRUE, 'Günlük internet kullanımı 15GB üzerinde'),
    ('R-02', 'spend_today_try > 300', 'SPEND_ALERT', 2, TRUE, 'Günlük harcama 300TL üzerinde'),
    ('R-03', 'content_minutes_today > 240', 'CONTENT_COOLDOWN_SUGGESTION', 4, TRUE, 'Günlük içerik tüketimi 4 saat üzerinde'),
    ('R-04', 'internet_today_gb > 15 AND spend_today_try > 300', 'CRITICAL_ALERT', 1, TRUE, 'Hem internet hem harcama yüksek - kritik'),
    ('R-05', 'internet_today_gb BETWEEN 10 AND 15', 'DATA_USAGE_NUDGE', 6, TRUE, 'Internet kullanımı orta seviyede'),
    ('R-06', 'spend_today_try BETWEEN 200 AND 300', 'SPEND_NUDGE', 5, TRUE, 'Harcama orta seviyede');

-- ============================================================
-- 3. USER STATE (Başlangıç durumu - sıfırlanmış)
-- Trigger ile eventlerden otomatik güncellenecek
-- ============================================================
INSERT INTO user_state (user_id, internet_today_gb, spend_today_try, content_minutes_today, risk_level) VALUES
    ('U1', 0.0, 0.0, 0.0, 'LOW'),
    ('U2', 0.0, 0.0, 0.0, 'LOW'),
    ('U3', 0.0, 0.0, 0.0, 'LOW'),
    ('U4', 0.0, 0.0, 0.0, 'LOW'),
    ('U5', 0.0, 0.0, 0.0, 'LOW');

-- ============================================================
-- 4. SAMPLE EVENTS
-- Not: Trigger sayesinde user_state otomatik güncellenecek
-- ============================================================

-- User 1 (Ayşe) Events
INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp) VALUES
    ('EVT-1001', 'U1', 'Superonline', 'USAGE', 6.4, 'GB', '2026-03-12T09:10:00Z'),
    ('EVT-1002', 'U1', 'TV+', 'CONTENT_CONSUMPTION', 70.0, 'MIN', '2026-03-12T12:30:00Z'),
    ('EVT-1003', 'U1', 'Superonline', 'USAGE', 9.1, 'GB', '2026-03-12T15:05:00Z'),
    ('EVT-1004', 'U1', 'Paycell', 'PAYMENT', 140.0, 'TRY', '2026-03-12T16:40:00Z'),
    ('EVT-1005', 'U1', 'Fizy', 'CONTENT_CONSUMPTION', 55.0, 'MIN', '2026-03-12T18:10:00Z');

-- User 2 (Ali) Events
INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp) VALUES
    ('EVT-2001', 'U2', 'Paycell', 'PAYMENT', 220.0, 'TRY', '2026-03-12T10:15:00Z'),
    ('EVT-2002', 'U2', 'Paycell', 'PAYMENT', 160.0, 'TRY', '2026-03-12T13:20:00Z'),
    ('EVT-2003', 'U2', 'Superonline', 'USAGE', 7.2, 'GB', '2026-03-12T14:55:00Z'),
    ('EVT-2004', 'U2', 'Game+', 'CONTENT_CONSUMPTION', 90.0, 'MIN', '2026-03-12T19:00:00Z');

-- User 3 (Deniz) Events
INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp) VALUES
    ('EVT-3001', 'U3', 'TV+', 'CONTENT_CONSUMPTION', 130.0, 'MIN', '2026-03-12T11:10:00Z'),
    ('EVT-3002', 'U3', 'Fizy', 'CONTENT_CONSUMPTION', 95.0, 'MIN', '2026-03-12T12:05:00Z'),
    ('EVT-3003', 'U3', 'Game+', 'CONTENT_CONSUMPTION', 85.0, 'MIN', '2026-03-12T20:30:00Z'),
    ('EVT-3004', 'U3', 'Superonline', 'USAGE', 5.0, 'GB', '2026-03-12T21:10:00Z');

-- User 4 (Mert) Events
INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp) VALUES
    ('EVT-4001', 'U4', 'Superonline', 'USAGE', 9.8, 'GB', '2026-03-12T09:40:00Z'),
    ('EVT-4002', 'U4', 'Paycell', 'PAYMENT', 90.0, 'TRY', '2026-03-12T17:25:00Z'),
    ('EVT-4003', 'U4', 'TV+', 'CONTENT_CONSUMPTION', 45.0, 'MIN', '2026-03-12T19:50:00Z');

-- User 5 (Ece) Events
INSERT INTO events (event_id, user_id, service, event_type, value, unit, timestamp) VALUES
    ('EVT-5001', 'U5', 'Superonline', 'USAGE', 8.3, 'GB', '2026-03-12T08:50:00Z'),
    ('EVT-5002', 'U5', 'Paycell', 'PAYMENT', 260.0, 'TRY', '2026-03-12T12:45:00Z'),
    ('EVT-5003', 'U5', 'Superonline', 'USAGE', 9.0, 'GB', '2026-03-12T17:10:00Z'),
    ('EVT-5004', 'U5', 'Paycell', 'PAYMENT', 160.0, 'TRY', '2026-03-12T18:05:00Z'),
    ('EVT-5005', 'U5', 'Fizy', 'CONTENT_CONSUMPTION', 40.0, 'MIN', '2026-03-12T21:40:00Z');

-- ============================================================
-- 5. SAMPLE DECISIONS (Örnek kararlar)
-- ============================================================
INSERT INTO decisions (decision_id, user_id, triggered_rules, selected_action, suppressed_actions, timestamp) VALUES
    ('D-900', 'U1', ARRAY['R-01'], 'DATA_USAGE_WARNING', NULL, '2026-03-12T22:00:00Z'),
    ('D-901', 'U2', ARRAY['R-02'], 'SPEND_ALERT', NULL, '2026-03-12T21:56:00Z'),
    ('D-902', 'U3', ARRAY['R-03'], 'CONTENT_COOLDOWN_SUGGESTION', NULL, '2026-03-12T21:52:00Z'),
    ('D-904', 'U5', ARRAY['R-04', 'R-02', 'R-01'], 'CRITICAL_ALERT', ARRAY['SPEND_ALERT', 'DATA_USAGE_WARNING']::action_type_enum[], '2026-03-12T21:44:00Z');

-- ============================================================
-- 6. SAMPLE ACTIONS (Gönderilen bildirimler)
-- ============================================================
INSERT INTO actions (action_id, user_id, action_type, message, created_at) VALUES
    ('A-1000', 'U1', 'DATA_USAGE_WARNING', 'Günlük internet kullanımınız 15GB''ı aştı. Kalan kotanızı kontrol etmenizi öneririz.', '2026-03-12T22:00:00Z'),
    ('A-1001', 'U2', 'SPEND_ALERT', 'Bugün toplam 380TL harcama yaptınız. Harcama limitinizi gözden geçirin.', '2026-03-12T21:56:00Z'),
    ('A-1002', 'U3', 'CONTENT_COOLDOWN_SUGGESTION', '4 saatten fazla içerik tükettiniz. Biraz ara vermeye ne dersiniz?', '2026-03-12T21:52:00Z'),
    ('A-1004', 'U5', 'CRITICAL_ALERT', 'Bugün internet ve harcama kullanımınız yüksek seviyededir. Limitlerinizi kontrol etmenizi öneririz.', '2026-03-12T21:44:00Z');

-- ============================================================
-- Seed data yükleme tamamlandı!
-- ============================================================

-- Doğrulama sorguları
SELECT 'Users:' AS info, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Events:', COUNT(*) FROM events
UNION ALL
SELECT 'Rules:', COUNT(*) FROM rules
UNION ALL
SELECT 'User States:', COUNT(*) FROM user_state
UNION ALL
SELECT 'Decisions:', COUNT(*) FROM decisions
UNION ALL
SELECT 'Actions:', COUNT(*) FROM actions;
