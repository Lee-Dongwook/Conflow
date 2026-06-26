-- ===========================================================================
-- RLS policies — manually applied. NOT part of alembic auto-migrations.
--
-- WHY MANUAL: enabling RLS on every workspace_uuid table at once is a
-- platform-wide flip. If service code somewhere forgets to call
-- `set_workspace_context`, that path returns empty results (USING) or
-- 403-style errors. We want this rollout deliberate.
--
-- APPLY:
--   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
--     -f alembic/manual_sql/rls_policies.sql
--
-- ROLLBACK: same file, run the "DROP POLICY / DISABLE" section at the bottom.
--
-- INVARIANT: every workspace_uuid table must appear here. If a new domain
-- table is added without a corresponding policy, multi-tenant isolation
-- depends solely on application-layer filters (Watch List #4 in
-- docs/02-product/domain-overview.md).
--
-- SESSION VARIABLES (set via `core/db_context.py:set_workspace_context`):
--   app.workspace_uuid - current tenant. Required for all per-tenant tables.
--   app.member_uuid    - resolved Member. Required only for the OneOnOne
--                        participant-only policy and future external-collab
--                        resource-scoped policies.
--   app.system_mode    - 'true' bypasses tenant filtering. Set ONLY by the
--                        outbox worker batch select (cross-workspace) and
--                        by maintenance jobs. Never by request handlers.
--   app.audit_mode     - 'true' lets Admin/Owner read OneOnOne notes after
--                        both-parties consent (Phase 3 — placeholder here).
-- ===========================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Shared Core
-- ---------------------------------------------------------------------------

ALTER TABLE members ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_members_workspace_isolation ON members
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_roles_workspace_isolation ON roles
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE role_assignments ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_role_assignments_workspace_isolation ON role_assignments
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_audit_logs_workspace_isolation ON audit_logs
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE entity_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_entity_links_workspace_isolation ON entity_links
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE event_outbox ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_event_outbox_workspace_isolation ON event_outbox
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

-- workspaces is the boundary itself — no policy, super only via app code.

-- ---------------------------------------------------------------------------
-- PM
-- ---------------------------------------------------------------------------

ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_issues_workspace_isolation ON issues
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_projects_workspace_isolation ON projects
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE pm_sprints ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_pm_sprints_workspace_isolation ON pm_sprints
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

-- ---------------------------------------------------------------------------
-- Comms
-- ---------------------------------------------------------------------------

ALTER TABLE channels ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_channels_workspace_isolation ON channels
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE channel_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_channel_members_workspace_isolation ON channel_members
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_messages_workspace_isolation ON messages
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

-- ---------------------------------------------------------------------------
-- HR
-- ---------------------------------------------------------------------------

ALTER TABLE employee_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_employee_profiles_workspace_isolation ON employee_profiles
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE org_units ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_org_units_workspace_isolation ON org_units
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE onboarding_workflows ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_onboarding_workflows_workspace_isolation ON onboarding_workflows
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE onboarding_steps ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_onboarding_steps_workspace_isolation ON onboarding_steps
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE offboarding_workflows ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_offboarding_workflows_workspace_isolation ON offboarding_workflows
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE leave_requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_leave_requests_workspace_isolation ON leave_requests
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

-- OneOnOne — workspace isolation AND participant-only.
-- See docs/04-architecture/data-model.md "rls_one_on_ones_participant_only".
ALTER TABLE one_on_ones ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_one_on_ones_participant_only ON one_on_ones
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR (
      workspace_uuid = current_setting('app.workspace_uuid')::uuid
      AND (
        manager_member_uuid = current_setting('app.member_uuid', true)::uuid
        OR report_member_uuid = current_setting('app.member_uuid', true)::uuid
        OR current_setting('app.audit_mode', true) = 'true'
      )
    )
  );

-- ---------------------------------------------------------------------------
-- Documents
-- ---------------------------------------------------------------------------

ALTER TABLE retention_policies ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_retention_policies_workspace_isolation ON retention_policies
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE document_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_document_templates_workspace_isolation ON document_templates
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE document_instances ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_document_instances_workspace_isolation ON document_instances
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

ALTER TABLE review_workflows ENABLE ROW LEVEL SECURITY;
CREATE POLICY rls_review_workflows_workspace_isolation ON review_workflows
  USING (
    current_setting('app.system_mode', true) = 'true'
    OR workspace_uuid = current_setting('app.workspace_uuid')::uuid
  );

COMMIT;

-- ===========================================================================
-- ROLLBACK BLOCK — run instead of the BEGIN..COMMIT above if you need to
-- disable RLS across the board (e.g. while investigating an isolation bug).
--
-- BEGIN;
--   ALTER TABLE members              DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS rls_members_workspace_isolation   ON members;
--   ALTER TABLE roles                DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS rls_roles_workspace_isolation     ON roles;
--   -- ... repeat for every table above ...
--   ALTER TABLE one_on_ones          DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS rls_one_on_ones_participant_only  ON one_on_ones;
-- COMMIT;
-- ===========================================================================
