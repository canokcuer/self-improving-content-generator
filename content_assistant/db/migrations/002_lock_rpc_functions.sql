-- Migration: 002_lock_rpc_functions.sql
-- Date: 2026-01-26
-- Description: Lock down RPC function permissions to prevent unauthorized access
-- Security Issue: RPC functions were callable by any role including anon

-- ============================================
-- Lock match_knowledge_chunks
-- Purpose: Vector similarity search for RAG
-- Access: authenticated + service_role
-- ============================================
REVOKE EXECUTE ON FUNCTION match_knowledge_chunks(vector(1024), float, int) FROM public;
REVOKE EXECUTE ON FUNCTION match_knowledge_chunks(vector(1024), float, int) FROM anon;
GRANT EXECUTE ON FUNCTION match_knowledge_chunks(vector(1024), float, int) TO authenticated;
GRANT EXECUTE ON FUNCTION match_knowledge_chunks(vector(1024), float, int) TO service_role;

-- ============================================
-- Lock match_content_generations
-- Purpose: Find similar content for few-shot learning
-- Access: authenticated + service_role
-- ============================================
REVOKE EXECUTE ON FUNCTION match_content_generations(vector(1024), int, int) FROM public;
REVOKE EXECUTE ON FUNCTION match_content_generations(vector(1024), int, int) FROM anon;
GRANT EXECUTE ON FUNCTION match_content_generations(vector(1024), int, int) TO authenticated;
GRANT EXECUTE ON FUNCTION match_content_generations(vector(1024), int, int) TO service_role;

-- ============================================
-- Lock get_cost_summary
-- Purpose: API cost reporting
-- Access: service_role ONLY (admin feature)
-- ============================================
REVOKE EXECUTE ON FUNCTION get_cost_summary(timestamp with time zone, timestamp with time zone) FROM public;
REVOKE EXECUTE ON FUNCTION get_cost_summary(timestamp with time zone, timestamp with time zone) FROM anon;
REVOKE EXECUTE ON FUNCTION get_cost_summary(timestamp with time zone, timestamp with time zone) FROM authenticated;
GRANT EXECUTE ON FUNCTION get_cost_summary(timestamp with time zone, timestamp with time zone) TO service_role;

-- ============================================
-- Verification Query
-- Run this to verify permissions are correct:
-- ============================================
-- SELECT
--     p.proname AS function_name,
--     r.rolname AS role,
--     has_function_privilege(r.rolname, p.oid, 'EXECUTE') AS can_execute
-- FROM pg_proc p
-- CROSS JOIN pg_roles r
-- WHERE p.proname IN ('match_knowledge_chunks', 'match_content_generations', 'get_cost_summary')
--   AND r.rolname IN ('anon', 'authenticated', 'service_role')
-- ORDER BY p.proname, r.rolname;
