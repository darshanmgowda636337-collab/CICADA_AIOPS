-- ==========================================
-- CICADA AIOPS DATABASE
-- SUPABASE POSTGRESQL
-- ==========================================

-- 1. TELEMETRY
CREATE TABLE IF NOT EXISTS public.telemetry (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    hostname TEXT,
    source TEXT,
    event_type TEXT,
    metric_name TEXT,
    metric_value DOUBLE PRECISION,
    severity TEXT,
    message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. INCIDENTS
CREATE TABLE IF NOT EXISTS public.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    source TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 3. ALERTS
CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES public.incidents(id)
        ON DELETE SET NULL,
    channel TEXT DEFAULT 'in_app',
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    delivery_status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. AUDIT LOGS
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id)
        ON DELETE SET NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_telemetry_hostname
ON public.telemetry(hostname);

CREATE INDEX IF NOT EXISTS idx_telemetry_created
ON public.telemetry(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_incidents_status
ON public.incidents(status);

CREATE INDEX IF NOT EXISTS idx_incidents_severity
ON public.incidents(severity);

CREATE INDEX IF NOT EXISTS idx_alerts_created
ON public.alerts(created_at DESC);

-- ENABLE RLS
ALTER TABLE public.telemetry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;