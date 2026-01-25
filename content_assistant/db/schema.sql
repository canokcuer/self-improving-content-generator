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

-- ============================================
-- NEW TABLES FOR AGENTIC ARCHITECTURE
-- ============================================

-- ============================================
-- Table 6: agent_configurations
-- Stores configuration for each sub-agent
-- ============================================
CREATE TABLE IF NOT EXISTS agent_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL UNIQUE,  -- 'orchestrator', 'wellness', 'storytelling', 'review'
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    model VARCHAR(100) DEFAULT 'claude-opus-4-5-20251101',
    temperature DECIMAL(3, 2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 1),
    max_tokens INTEGER DEFAULT 4096,
    tools_enabled JSONB DEFAULT '[]',  -- List of tool names this agent can use
    knowledge_sources TEXT[] DEFAULT '{}',  -- Which knowledge folders/files this agent accesses
    is_active BOOLEAN DEFAULT TRUE,
    execution_order INTEGER DEFAULT 0,  -- Order in sequential execution (1=first)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default agent configurations
INSERT INTO agent_configurations (agent_name, display_name, description, system_prompt, execution_order, knowledge_sources, tools_enabled) VALUES
('orchestrator', 'Orchestrator Agent', 'Conducts conversational briefing with users until fully aligned on content requirements',
'You are the Orchestrator Agent for TheLifeCo Content Assistant. Your role is to have a natural conversation with users to understand their content needs. Ask clarifying questions until you are 100% aligned with what they want. Detect the marketing funnel stage (awareness, consideration, conversion, loyalty). Be helpful, not interrogative. Validate understanding before proceeding.',
1, ARRAY['orchestrator'], '["search_knowledge", "get_similar_content", "clarify_intent", "suggest_approach"]'),

('wellness', 'Wellness Verification Agent', 'Verifies content against TheLifeCo knowledge base for factual accuracy',
'You are the Wellness Verification Agent. Your role is to verify all facts, claims, program details, and center information against the TheLifeCo knowledge base. Flag any inaccuracies or unverified claims. Provide supporting evidence for verified facts.',
2, ARRAY['wellness', 'wellness/centers'], '["search_wellness_knowledge", "verify_program_info", "verify_claim", "get_center_info"]'),

('storytelling', 'Storytelling Agent', 'Creates engaging content using hooks, emotional journeys, and platform optimization',
'You are the Storytelling Agent for TheLifeCo. Your role is to create compelling, engaging content that captures attention and drives action. Use proven hook patterns, create open loops for engagement, and optimize for the target platform. Match content style to the funnel stage.',
3, ARRAY['storytelling', 'brand'], '["get_hook_patterns", "get_engagement_tactics", "get_platform_rules", "get_few_shot_examples", "get_cta_templates"]'),

('review', 'Review & Learning Agent', 'Collects feedback, extracts learnings, and manages admin review queue',
'You are the Review & Learning Agent. Your role is to collect user feedback, extract actionable learnings, and queue insights for admin approval. Identify patterns in feedback that can improve future generations.',
4, ARRAY[]::TEXT[], '["store_feedback", "extract_learning", "queue_for_review"]')

ON CONFLICT (agent_name) DO NOTHING;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_agent_configurations_updated_at ON agent_configurations;
CREATE TRIGGER update_agent_configurations_updated_at
    BEFORE UPDATE ON agent_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Table 7: agent_learnings
-- Stores learnings extracted from feedback for continuous improvement
-- ============================================
CREATE TABLE IF NOT EXISTS agent_learnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL,  -- Which agent learned this
    learning_type VARCHAR(50) NOT NULL CHECK (learning_type IN ('pattern', 'preference', 'correction', 'feedback', 'style')),
    learning_content TEXT NOT NULL,  -- What was learned
    learning_summary VARCHAR(500),  -- Short summary for display
    source_generation_id UUID REFERENCES content_generations(id) ON DELETE SET NULL,
    source_feedback_id UUID,  -- References feedback_reviews.id
    confidence_score DECIMAL(3, 2) DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    times_applied INTEGER DEFAULT 0,  -- How often this learning was used
    success_rate DECIMAL(3, 2) CHECK (success_rate >= 0 AND success_rate <= 1),  -- Success rate when applied
    is_approved BOOLEAN DEFAULT FALSE,  -- Admin-approved learning
    approved_by UUID,  -- Admin user who approved
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,  -- If rejected, why
    tags TEXT[] DEFAULT '{}',  -- Categorization tags
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for agent_learnings
CREATE INDEX IF NOT EXISTS agent_learnings_agent_name_idx ON agent_learnings(agent_name);
CREATE INDEX IF NOT EXISTS agent_learnings_learning_type_idx ON agent_learnings(learning_type);
CREATE INDEX IF NOT EXISTS agent_learnings_is_approved_idx ON agent_learnings(is_approved);
CREATE INDEX IF NOT EXISTS agent_learnings_confidence_idx ON agent_learnings(confidence_score);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_agent_learnings_updated_at ON agent_learnings;
CREATE TRIGGER update_agent_learnings_updated_at
    BEFORE UPDATE ON agent_learnings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Table 8: feedback_reviews
-- Detailed feedback storage with admin review workflow
-- ============================================
CREATE TABLE IF NOT EXISTS feedback_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID NOT NULL REFERENCES content_generations(id) ON DELETE CASCADE,
    user_id UUID,

    -- User feedback
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,  -- Open-ended feedback field
    what_worked TEXT[] DEFAULT '{}',
    what_needs_work TEXT[] DEFAULT '{}',

    -- Structured feedback categories
    hook_feedback VARCHAR(20) CHECK (hook_feedback IN ('excellent', 'good', 'needs_work', 'poor')),
    facts_feedback VARCHAR(20) CHECK (facts_feedback IN ('accurate', 'mostly_accurate', 'some_issues', 'inaccurate')),
    tone_feedback VARCHAR(20) CHECK (tone_feedback IN ('perfect', 'good', 'off_brand', 'wrong')),
    cta_feedback VARCHAR(20) CHECK (cta_feedback IN ('compelling', 'good', 'weak', 'missing')),

    -- Admin review workflow
    admin_review_status VARCHAR(20) DEFAULT 'pending' CHECK (admin_review_status IN ('pending', 'in_review', 'reviewed', 'approved', 'rejected')),
    admin_reviewer_id UUID,
    admin_notes TEXT,
    admin_reviewed_at TIMESTAMP WITH TIME ZONE,

    -- Learning extraction
    learnings_extracted BOOLEAN DEFAULT FALSE,
    extracted_learning_ids UUID[] DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for feedback_reviews
CREATE INDEX IF NOT EXISTS feedback_reviews_generation_idx ON feedback_reviews(generation_id);
CREATE INDEX IF NOT EXISTS feedback_reviews_user_idx ON feedback_reviews(user_id);
CREATE INDEX IF NOT EXISTS feedback_reviews_admin_status_idx ON feedback_reviews(admin_review_status);
CREATE INDEX IF NOT EXISTS feedback_reviews_rating_idx ON feedback_reviews(rating);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_feedback_reviews_updated_at ON feedback_reviews;
CREATE TRIGGER update_feedback_reviews_updated_at
    BEFORE UPDATE ON feedback_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Table 9: conversations
-- Stores persistent conversations for "forever conversation" feature
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255),  -- Auto-generated or user-set
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),

    -- Conversation content
    messages JSONB DEFAULT '[]'::jsonb,  -- Array of message objects

    -- Agent state
    current_agent VARCHAR(50),  -- Which agent is currently active
    agent_state JSONB DEFAULT '{}',  -- Current state of agent execution
    brief_data JSONB,  -- Extracted brief from conversation

    -- Metadata
    funnel_stage VARCHAR(20) CHECK (funnel_stage IN ('awareness', 'consideration', 'conversion', 'loyalty')),
    platform VARCHAR(50),
    content_type VARCHAR(50),
    generation_ids UUID[] DEFAULT '{}',  -- Linked content generations

    -- Campaign info (collected dynamically)
    campaign_info JSONB DEFAULT '{}',  -- {has_campaign: bool, price: string, duration: string, center: string}

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for conversations
CREATE INDEX IF NOT EXISTS conversations_user_idx ON conversations(user_id);
CREATE INDEX IF NOT EXISTS conversations_status_idx ON conversations(status);
CREATE INDEX IF NOT EXISTS conversations_created_at_idx ON conversations(created_at DESC);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Backfill: ensure messages is JSONB array (not JSONB[])
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'conversations'
          AND column_name = 'messages'
          AND udt_name = '_jsonb'
    ) THEN
        ALTER TABLE conversations
            ALTER COLUMN messages TYPE JSONB
            USING to_jsonb(messages);
    END IF;

    ALTER TABLE conversations
        ALTER COLUMN messages SET DEFAULT '[]'::jsonb;
END $$;

-- ============================================
-- Table 10: user_roles
-- Role-based access control for admin features
-- ============================================
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'editor', 'admin', 'super_admin')),
    permissions JSONB DEFAULT '{}',  -- Additional granular permissions
    granted_by UUID,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_user_roles_updated_at ON user_roles;
CREATE TRIGGER update_user_roles_updated_at
    BEFORE UPDATE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Function: Get approved learnings for an agent
-- ============================================
CREATE OR REPLACE FUNCTION get_agent_learnings(
    p_agent_name VARCHAR(50),
    p_learning_type VARCHAR(50) DEFAULT NULL,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    learning_type VARCHAR(50),
    learning_content TEXT,
    learning_summary VARCHAR(500),
    confidence_score DECIMAL(3, 2),
    times_applied INTEGER,
    success_rate DECIMAL(3, 2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        al.id,
        al.learning_type,
        al.learning_content,
        al.learning_summary,
        al.confidence_score,
        al.times_applied,
        al.success_rate
    FROM agent_learnings al
    WHERE al.agent_name = p_agent_name
      AND al.is_approved = TRUE
      AND (p_learning_type IS NULL OR al.learning_type = p_learning_type)
    ORDER BY al.confidence_score DESC, al.success_rate DESC NULLS LAST
    LIMIT p_limit;
END;
$$;

-- ============================================
-- Function: Check if user is admin
-- ============================================
CREATE OR REPLACE FUNCTION is_user_admin(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    user_role VARCHAR(20);
BEGIN
    SELECT role INTO user_role
    FROM user_roles
    WHERE user_id = p_user_id;

    RETURN user_role IN ('admin', 'super_admin');
END;
$$;

-- ============================================
-- RLS Policies for new tables
-- ============================================

-- Enable RLS
ALTER TABLE agent_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_learnings ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY "Service role has full access to agent_configurations"
ON agent_configurations FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role has full access to agent_learnings"
ON agent_learnings FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role has full access to feedback_reviews"
ON feedback_reviews FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role has full access to conversations"
ON conversations FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role has full access to user_roles"
ON user_roles FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated user policies for agent_configurations (read-only)
CREATE POLICY "Authenticated users can read agent_configurations"
ON agent_configurations FOR SELECT TO authenticated USING (true);

-- Authenticated user policies for agent_learnings (read approved only)
CREATE POLICY "Authenticated users can read approved learnings"
ON agent_learnings FOR SELECT TO authenticated USING (is_approved = TRUE);

-- Authenticated user policies for feedback_reviews
CREATE POLICY "Users can read their own feedback"
ON feedback_reviews FOR SELECT TO authenticated USING (user_id = auth.uid());

CREATE POLICY "Users can insert feedback"
ON feedback_reviews FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own feedback"
ON feedback_reviews FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- Authenticated user policies for conversations
CREATE POLICY "Users can read their own conversations"
ON conversations FOR SELECT TO authenticated USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own conversations"
ON conversations FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own conversations"
ON conversations FOR UPDATE TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete their own conversations"
ON conversations FOR DELETE TO authenticated USING (user_id = auth.uid());

-- User roles - users can only see their own role
CREATE POLICY "Users can read their own role"
ON user_roles FOR SELECT TO authenticated USING (user_id = auth.uid());
