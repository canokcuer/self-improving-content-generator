-- TheLifeCo Content Assistant Database Schema
-- Run this in Supabase SQL Editor to set up the database

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Table 1: knowledge_chunks
-- Stores embedded knowledge base content for RAG
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1024),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Prevent duplicate chunks from same source
    UNIQUE(source, chunk_index)
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for source filtering
CREATE INDEX IF NOT EXISTS knowledge_chunks_source_idx ON knowledge_chunks(source);

-- ============================================
-- Table 2: content_generations
-- Stores generated content with signals for learning
-- ============================================
CREATE TABLE IF NOT EXISTS content_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content Brief (13 Socratic questions)
    brief JSONB NOT NULL,

    -- Generated Content
    preview JSONB,  -- hook, hook_type, open_loops, promise
    content TEXT,
    platform VARCHAR(50) NOT NULL,
    content_type VARCHAR(50) NOT NULL,

    -- Signals for learning
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    what_worked TEXT[],
    what_needs_work TEXT[],
    was_approved BOOLEAN DEFAULT FALSE,
    was_regenerated BOOLEAN DEFAULT FALSE,
    manual_edits TEXT,

    -- Embedding for similarity search
    brief_embedding vector(1024),
    content_embedding vector(1024),

    -- Metadata
    user_id UUID,
    experiment_id UUID,
    variant VARCHAR(50),
    api_cost_usd DECIMAL(10, 6),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for finding similar past generations
CREATE INDEX IF NOT EXISTS content_generations_brief_embedding_idx
ON content_generations USING ivfflat (brief_embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for platform/type filtering
CREATE INDEX IF NOT EXISTS content_generations_platform_idx ON content_generations(platform);
CREATE INDEX IF NOT EXISTS content_generations_content_type_idx ON content_generations(content_type);
CREATE INDEX IF NOT EXISTS content_generations_rating_idx ON content_generations(rating);

-- ============================================
-- Table 3: experiments
-- A/B experiment definitions
-- ============================================
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    variants JSONB NOT NULL,  -- {"control": {...}, "treatment": {...}}
    traffic_split JSONB NOT NULL,  -- {"control": 0.5, "treatment": 0.5}
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'running', 'paused', 'completed')),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Table 4: experiment_assignments
-- Tracks which users are assigned to which experiments
-- ============================================
CREATE TABLE IF NOT EXISTS experiment_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    variant VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- One assignment per user per experiment
    UNIQUE(experiment_id, user_id)
);

CREATE INDEX IF NOT EXISTS experiment_assignments_experiment_idx ON experiment_assignments(experiment_id);
CREATE INDEX IF NOT EXISTS experiment_assignments_user_idx ON experiment_assignments(user_id);

-- ============================================
-- Table 5: api_costs
-- Track API usage and costs for budget management
-- ============================================
CREATE TABLE IF NOT EXISTS api_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service VARCHAR(50) NOT NULL,  -- 'anthropic', 'voyage'
    operation VARCHAR(100) NOT NULL,  -- 'generate_content', 'embed_text', etc.
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for cost aggregation queries
CREATE INDEX IF NOT EXISTS api_costs_service_idx ON api_costs(service);
CREATE INDEX IF NOT EXISTS api_costs_created_at_idx ON api_costs(created_at);

-- ============================================
-- Function: Update timestamp trigger
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
DROP TRIGGER IF EXISTS update_knowledge_chunks_updated_at ON knowledge_chunks;
CREATE TRIGGER update_knowledge_chunks_updated_at
    BEFORE UPDATE ON knowledge_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_content_generations_updated_at ON content_generations;
CREATE TRIGGER update_content_generations_updated_at
    BEFORE UPDATE ON content_generations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_experiments_updated_at ON experiments;
CREATE TRIGGER update_experiments_updated_at
    BEFORE UPDATE ON experiments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Function: Vector similarity search for knowledge
-- ============================================
CREATE OR REPLACE FUNCTION match_knowledge_chunks(
    query_embedding vector(1024),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    source VARCHAR(255),
    chunk_index INTEGER,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kc.id,
        kc.content,
        kc.source,
        kc.chunk_index,
        kc.metadata,
        1 - (kc.embedding <=> query_embedding) AS similarity
    FROM knowledge_chunks kc
    WHERE kc.embedding IS NOT NULL
      AND 1 - (kc.embedding <=> query_embedding) > match_threshold
    ORDER BY kc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- Function: Find similar past generations for few-shot
-- ============================================
CREATE OR REPLACE FUNCTION match_content_generations(
    query_embedding vector(1024),
    min_rating INT DEFAULT 4,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    brief JSONB,
    content TEXT,
    platform VARCHAR(50),
    rating INTEGER,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        cg.id,
        cg.brief,
        cg.content,
        cg.platform,
        cg.rating,
        1 - (cg.brief_embedding <=> query_embedding) AS similarity
    FROM content_generations cg
    WHERE cg.brief_embedding IS NOT NULL
      AND cg.rating >= min_rating
      AND cg.was_approved = TRUE
    ORDER BY cg.brief_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================
-- Function: Get daily/monthly cost totals
-- ============================================
CREATE OR REPLACE FUNCTION get_cost_summary(
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE (
    service VARCHAR(50),
    total_cost DECIMAL(10, 6),
    total_tokens_input BIGINT,
    total_tokens_output BIGINT,
    operation_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ac.service,
        SUM(ac.cost_usd) AS total_cost,
        SUM(ac.tokens_input)::BIGINT AS total_tokens_input,
        SUM(ac.tokens_output)::BIGINT AS total_tokens_output,
        COUNT(*)::BIGINT AS operation_count
    FROM api_costs ac
    WHERE ac.created_at >= start_date
      AND ac.created_at < end_date
    GROUP BY ac.service;
END;
$$;

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS on all tables
ALTER TABLE knowledge_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiment_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_costs ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (for admin operations)
CREATE POLICY "Service role has full access to knowledge_chunks"
ON knowledge_chunks FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role has full access to content_generations"
ON content_generations FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role has full access to experiments"
ON experiments FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role has full access to experiment_assignments"
ON experiment_assignments FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY "Service role has full access to api_costs"
ON api_costs FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Allow authenticated users to read knowledge chunks
CREATE POLICY "Authenticated users can read knowledge_chunks"
ON knowledge_chunks FOR SELECT
TO authenticated
USING (true);

-- Allow authenticated users to manage their own content generations
CREATE POLICY "Users can read all content_generations"
ON content_generations FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Users can insert content_generations"
ON content_generations FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Users can update their own content_generations"
ON content_generations FOR UPDATE
TO authenticated
USING (user_id = auth.uid() OR user_id IS NULL)
WITH CHECK (user_id = auth.uid() OR user_id IS NULL);

-- Allow authenticated users to read experiments and their assignments
CREATE POLICY "Authenticated users can read experiments"
ON experiments FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Authenticated users can read their assignments"
ON experiment_assignments FOR SELECT
TO authenticated
USING (user_id = auth.uid());
