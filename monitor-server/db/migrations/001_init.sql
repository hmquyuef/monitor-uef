-- 1. Create Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    hostname VARCHAR(255),
    ip_address INET,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'offline',
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Metrics Table (Time-Series)
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cpu_percent NUMERIC(5,2),
    cpu_cores SMALLINT,
    cpu_freq_mhz NUMERIC(8,2),
    ram_total BIGINT,
    ram_used BIGINT,
    ram_percent NUMERIC(5,2),
    swap_total BIGINT,
    swap_used BIGINT,
    disk_total BIGINT,
    disk_used BIGINT,
    disk_percent NUMERIC(5,2),
    disk_read_bps BIGINT,
    disk_write_bps BIGINT,
    net_bytes_sent BIGINT,
    net_bytes_recv BIGINT,
    extra_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_metrics_agent_time ON metrics(agent_id, collected_at DESC);

-- 3. Create Alert Configs Table
CREATE TABLE IF NOT EXISTS alert_configs (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- cpu, ram, disk
    warning_threshold NUMERIC(5,2),
    critical_threshold NUMERIC(5,2),
    duration_seconds INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, metric_type)
);

-- 4. Create Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_type VARCHAR(50),
    severity VARCHAR(20),
    threshold NUMERIC(5,2),
    value NUMERIC(5,2),
    message TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    notified_telegram BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert Default Settings
INSERT INTO system_settings (key, value) VALUES ('telegram_bot_token', '') ON CONFLICT DO NOTHING;
INSERT INTO system_settings (key, value) VALUES ('telegram_chat_id', '') ON CONFLICT DO NOTHING;
INSERT INTO system_settings (key, value) VALUES ('alert_cooldown_minutes', '5') ON CONFLICT DO NOTHING;
