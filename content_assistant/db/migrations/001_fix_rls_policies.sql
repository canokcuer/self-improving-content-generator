-- Migration: 001_fix_rls_policies.sql
-- Date: 2026-01-26
-- Description: Fix overly permissive RLS policies on content_generations table
-- Security Issue: Users could previously read ALL content_generations regardless of ownership

-- ============================================
-- Step 1: Drop the overly permissive policies
-- ============================================

DROP POLICY IF EXISTS "Users can read all content_generations" ON content_generations;
DROP POLICY IF EXISTS "Users can insert content_generations" ON content_generations;
DROP POLICY IF EXISTS "Users can update their own content_generations" ON content_generations;

-- ============================================
-- Step 2: Create secure owner-only policies
-- ============================================

-- SELECT: Users can only read their own content generations
CREATE POLICY "Users can read their own content_generations"
ON content_generations FOR SELECT
TO authenticated
USING (user_id = auth.uid());

-- INSERT: Users can only insert with their own user_id
CREATE POLICY "Users can insert their own content_generations"
ON content_generations FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

-- UPDATE: Users can only update their own content (removed NULL bypass vulnerability)
CREATE POLICY "Users can update their own content_generations"
ON content_generations FOR UPDATE
TO authenticated
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- DELETE: Users can only delete their own content (new policy)
CREATE POLICY "Users can delete their own content_generations"
ON content_generations FOR DELETE
TO authenticated
USING (user_id = auth.uid());

-- ============================================
-- Step 3: Verify policies are in place
-- ============================================

-- Run this query to verify:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies
-- WHERE tablename = 'content_generations';

-- ============================================
-- Rollback (if needed):
-- ============================================
-- DROP POLICY IF EXISTS "Users can read their own content_generations" ON content_generations;
-- DROP POLICY IF EXISTS "Users can insert their own content_generations" ON content_generations;
-- DROP POLICY IF EXISTS "Users can update their own content_generations" ON content_generations;
-- DROP POLICY IF EXISTS "Users can delete their own content_generations" ON content_generations;
--
-- Then recreate old policies (NOT RECOMMENDED - security vulnerability):
-- CREATE POLICY "Users can read all content_generations" ON content_generations FOR SELECT TO authenticated USING (true);
-- CREATE POLICY "Users can insert content_generations" ON content_generations FOR INSERT TO authenticated WITH CHECK (true);
-- CREATE POLICY "Users can update their own content_generations" ON content_generations FOR UPDATE TO authenticated USING (user_id = auth.uid() OR user_id IS NULL) WITH CHECK (user_id = auth.uid() OR user_id IS NULL);
