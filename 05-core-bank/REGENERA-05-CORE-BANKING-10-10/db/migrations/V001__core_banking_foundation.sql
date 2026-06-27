-- =============================================================================
-- CORE BANKING — FUNDAÇÃO CONTÁBIL E OPERACIONAL
-- =============================================================================

-- saldo não é coluna de conveniência.
-- saldo é consequência do razão.
-- quem edita saldo fora do ledger apaga a causa e preserva só o efeito.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS core_banking;
SET search_path TO core_banking, public;

CREATE TYPE account_class AS ENUM (
  'ASSET',
  'LIABILITY',
  'EQUITY',
  'REVENUE',
  'EXPENSE'
);

CREATE TYPE account_status AS ENUM (
  'OPEN',
  'BLOCKED',
  'CLOSED'
);

CREATE TYPE posting_side AS ENUM (
  'DEBIT',
  'CREDIT'
);

CREATE TYPE entry_status AS ENUM (
  'DRAFT',
  'POSTED'
);

CREATE TYPE hold_status AS ENUM (
  'ACTIVE',
  'CONSUMED',
  'RELEASED',
  'EXPIRED'
);

CREATE TYPE idempotency_state AS ENUM (
  'RECEIVED',
  'PROCESSING',
  'COMPLETED',
  'FAILED_RETRYABLE',
  'FAILED_FINAL',
  'UNKNOWN',
  'EXPIRED'
);

CREATE TYPE payment_status AS ENUM (
  'RECEIVED',
  'VALIDATED',
  'AUTHORIZED',
  'DEBITED',
  'SENT',
  'SETTLED',
  'FAILED',
  'UNKNOWN',
  'RECONCILIATION_REQUIRED',
  'REVERSED'
);

-- -----------------------------------------------------------------------------
-- 1. CONTAS CONTÁBEIS
-- -----------------------------------------------------------------------------

CREATE TABLE ledger_accounts (

  id              uuid PRIMARY KEY,
  owner_id        uuid NOT NULL,

  account_class   account_class NOT NULL,
  currency        char(3) NOT NULL
                  CHECK (currency ~ '^[A-Z]{3}$'),

  status          account_status NOT NULL DEFAULT 'OPEN',

  created_at      timestamptz NOT NULL DEFAULT now(),
  blocked_at      timestamptz,
  closed_at       timestamptz,

  CONSTRAINT ck_ledger_accounts_closed_at
    CHECK (
      (status = 'CLOSED' AND closed_at IS NOT NULL)
      OR
      (status <> 'CLOSED' AND closed_at IS NULL)
    )

);

CREATE INDEX ix_ledger_accounts_owner
  ON ledger_accounts(owner_id, status);

-- -----------------------------------------------------------------------------
-- 2. LANÇAMENTO E PARTIDAS
-- -----------------------------------------------------------------------------

-- lançamento nasce DRAFT porque as pernas ainda não chegaram.
-- POSTED é o ponto sem volta.
-- depois disso, correção só entra como nova partida compensatória.

CREATE TABLE journal_entries (

  id                uuid PRIMARY KEY,

  idempotency_key   varchar(128) NOT NULL UNIQUE,
  business_event    varchar(80) NOT NULL
                    CHECK (business_event ~ '^[A-Z][A-Z0-9_]{2,79}$'),

  description       varchar(200) NOT NULL,
  accounting_date   date NOT NULL,
  occurred_at       timestamptz NOT NULL,

  status            entry_status NOT NULL DEFAULT 'DRAFT',
  finalized_at      timestamptz,

  reversal_of       uuid UNIQUE
                    REFERENCES journal_entries(id),

  immutable_hash    char(64) NOT NULL
                    CHECK (immutable_hash ~ '^[a-f0-9]{64}$'),

  created_at        timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT ck_journal_entries_finalized
    CHECK (
      (status = 'POSTED' AND finalized_at IS NOT NULL)
      OR
      (status = 'DRAFT' AND finalized_at IS NULL)
    )

);

CREATE TABLE ledger_postings (

  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entry_id          uuid NOT NULL
                    REFERENCES journal_entries(id),

  line_seq          smallint NOT NULL
                    CHECK (line_seq BETWEEN 1 AND 200),

  account_id        uuid NOT NULL
                    REFERENCES ledger_accounts(id),

  side              posting_side NOT NULL,

  amount_minor      bigint NOT NULL
                    CHECK (amount_minor > 0),

  currency          char(3) NOT NULL
                    CHECK (currency ~ '^[A-Z]{3}$'),

  created_at        timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT uq_ledger_postings_entry_line
    UNIQUE (entry_id, line_seq)

);

CREATE INDEX ix_ledger_postings_account
  ON ledger_postings(account_id, entry_id);

CREATE OR REPLACE FUNCTION ensure_posting_targets_draft_entry()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  current_status entry_status;
  account_currency char(3);
BEGIN
  SELECT status
    INTO current_status
    FROM journal_entries
   WHERE id = NEW.entry_id
   FOR UPDATE;

  IF current_status IS NULL THEN
    RAISE EXCEPTION 'LEDGER_ENTRY_NOT_FOUND';
  END IF;

  IF current_status <> 'DRAFT' THEN
    RAISE EXCEPTION 'LEDGER_ENTRY_ALREADY_POSTED';
  END IF;

  SELECT currency
    INTO account_currency
    FROM ledger_accounts
   WHERE id = NEW.account_id;

  IF account_currency IS NULL THEN
    RAISE EXCEPTION 'LEDGER_ACCOUNT_NOT_FOUND';
  END IF;

  IF account_currency <> NEW.currency THEN
    RAISE EXCEPTION 'LEDGER_ACCOUNT_CURRENCY_MISMATCH';
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_posting_requires_draft_entry
BEFORE INSERT ON ledger_postings
FOR EACH ROW
EXECUTE FUNCTION ensure_posting_targets_draft_entry();

CREATE OR REPLACE FUNCTION assert_balanced_entry()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  line_count integer;
  currency_count integer;
  debit_total numeric(38,0);
  credit_total numeric(38,0);
BEGIN
  IF NEW.status <> 'POSTED' THEN
    RETURN NEW;
  END IF;

  SELECT
    count(*),
    count(DISTINCT currency),
    COALESCE(sum(amount_minor) FILTER (WHERE side = 'DEBIT'), 0),
    COALESCE(sum(amount_minor) FILTER (WHERE side = 'CREDIT'), 0)
  INTO
    line_count,
    currency_count,
    debit_total,
    credit_total
  FROM ledger_postings
  WHERE entry_id = NEW.id;

  IF line_count < 2 THEN
    RAISE EXCEPTION 'LEDGER_MIN_TWO_LINES';
  END IF;

  IF currency_count <> 1 THEN
    RAISE EXCEPTION 'LEDGER_MIXED_CURRENCY';
  END IF;

  IF debit_total <> credit_total THEN
    RAISE EXCEPTION 'LEDGER_UNBALANCED';
  END IF;

  RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_journal_entry_must_balance
AFTER UPDATE OF status ON journal_entries
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION assert_balanced_entry();

CREATE OR REPLACE FUNCTION protect_posted_entry()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'LEDGER_DELETE_FORBIDDEN';
  END IF;

  IF OLD.status = 'POSTED' THEN
    RAISE EXCEPTION 'LEDGER_POSTED_ENTRY_IMMUTABLE';
  END IF;

  IF NEW.status = 'POSTED'
     AND OLD.status = 'DRAFT'
     AND NEW.id = OLD.id
     AND NEW.idempotency_key = OLD.idempotency_key
     AND NEW.business_event = OLD.business_event
     AND NEW.description = OLD.description
     AND NEW.accounting_date = OLD.accounting_date
     AND NEW.occurred_at = OLD.occurred_at
     AND NEW.reversal_of IS NOT DISTINCT FROM OLD.reversal_of
     AND NEW.immutable_hash = OLD.immutable_hash
  THEN
    RETURN NEW;
  END IF;

  RAISE EXCEPTION 'LEDGER_ENTRY_MUTATION_FORBIDDEN';
END;
$$;

CREATE TRIGGER trg_protect_journal_entries
BEFORE UPDATE OR DELETE ON journal_entries
FOR EACH ROW
EXECUTE FUNCTION protect_posted_entry();

CREATE OR REPLACE FUNCTION forbid_posting_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'LEDGER_POSTING_IMMUTABLE';
END;
$$;

CREATE TRIGGER trg_postings_immutable
BEFORE UPDATE OR DELETE ON ledger_postings
FOR EACH ROW
EXECUTE FUNCTION forbid_posting_mutation();

-- -----------------------------------------------------------------------------
-- 3. RESERVAS
-- -----------------------------------------------------------------------------

CREATE TABLE account_holds (

  id              uuid PRIMARY KEY,
  account_id      uuid NOT NULL
                  REFERENCES ledger_accounts(id),

  amount_minor    bigint NOT NULL
                  CHECK (amount_minor > 0),
  currency        char(3) NOT NULL,

  reason          varchar(200) NOT NULL,
  status          hold_status NOT NULL DEFAULT 'ACTIVE',

  created_at      timestamptz NOT NULL,
  expires_at      timestamptz NOT NULL,
  closed_at       timestamptz,

  CONSTRAINT ck_account_holds_expiry
    CHECK (expires_at > created_at),

  CONSTRAINT ck_account_holds_closed_at
    CHECK (
      (status = 'ACTIVE' AND closed_at IS NULL)
      OR
      (status <> 'ACTIVE' AND closed_at IS NOT NULL)
    )

);

CREATE INDEX ix_account_holds_active
  ON account_holds(account_id, expires_at)
  WHERE status = 'ACTIVE';

-- -----------------------------------------------------------------------------
-- 4. IDEMPOTÊNCIA
-- -----------------------------------------------------------------------------

-- se a mesma chave aparece com outro payload, não é retry.
-- é conflito.

CREATE TABLE idempotency_records (

  scope               varchar(80) NOT NULL,
  idempotency_key     varchar(128) NOT NULL,

  payload_hash        char(64) NOT NULL
                      CHECK (payload_hash ~ '^[a-f0-9]{64}$'),

  state               idempotency_state NOT NULL,
  response_reference  varchar(200),

  lease_until         timestamptz,
  expires_at          timestamptz,

  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now(),

  PRIMARY KEY (scope, idempotency_key),

  CONSTRAINT ck_idempotency_completed_response
    CHECK (
      (state = 'COMPLETED' AND response_reference IS NOT NULL)
      OR
      (state <> 'COMPLETED')
    )

);

CREATE INDEX ix_idempotency_state
  ON idempotency_records(state, lease_until);

-- -----------------------------------------------------------------------------
-- 5. PAGAMENTOS E PIX
-- -----------------------------------------------------------------------------

CREATE TABLE payments (

  id                  uuid PRIMARY KEY,

  sender_account_id   uuid NOT NULL
                      REFERENCES ledger_accounts(id),
  clearing_account_id uuid NOT NULL
                      REFERENCES ledger_accounts(id),

  amount_minor        bigint NOT NULL
                      CHECK (amount_minor > 0),
  currency            char(3) NOT NULL,

  status              payment_status NOT NULL,

  ledger_entry_id     uuid UNIQUE
                      REFERENCES journal_entries(id),
  reversal_entry_id   uuid UNIQUE
                      REFERENCES journal_entries(id),

  correlation_id      uuid NOT NULL,

  created_at          timestamptz NOT NULL,
  updated_at          timestamptz NOT NULL,

  CONSTRAINT ck_payments_reversal
    CHECK (
      (status = 'REVERSED' AND reversal_entry_id IS NOT NULL)
      OR
      (status <> 'REVERSED')
    )

);

CREATE INDEX ix_payments_status
  ON payments(status, updated_at);

CREATE TABLE pix_payments (

  payment_id             uuid PRIMARY KEY
                         REFERENCES payments(id),

  internal_end_to_end_id char(32) NOT NULL UNIQUE,
  external_end_to_end_id varchar(64) UNIQUE,

  receiver_key_masked    varchar(160) NOT NULL,
  receiver_key_hash      char(64) NOT NULL
                         CHECK (receiver_key_hash ~ '^[a-f0-9]{64}$'),
  receiver_ispb          char(8),

  created_at             timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT ck_pix_internal_e2e
    CHECK (internal_end_to_end_id ~ '^E[0-9]{8}[0-9]{12}[a-z0-9]{11}$'),

  CONSTRAINT ck_pix_receiver_ispb
    CHECK (receiver_ispb IS NULL OR receiver_ispb ~ '^[0-9]{8}$')

);

-- -----------------------------------------------------------------------------
-- 6. OUTBOX E RECONCILIAÇÃO
-- -----------------------------------------------------------------------------

CREATE TABLE outbox_events (

  id              uuid PRIMARY KEY,
  aggregate_type  varchar(80) NOT NULL,
  aggregate_id    uuid NOT NULL,
  event_type      varchar(80) NOT NULL,
  payload         jsonb NOT NULL,

  occurred_at     timestamptz NOT NULL,
  published_at    timestamptz,

  attempts        integer NOT NULL DEFAULT 0
                  CHECK (attempts >= 0),
  next_attempt_at timestamptz,
  last_error      varchar(500)

);

CREATE INDEX ix_outbox_pending
  ON outbox_events(next_attempt_at, occurred_at)
  WHERE published_at IS NULL;

CREATE TABLE reconciliation_cases (

  id                  uuid PRIMARY KEY,
  payment_id          uuid NOT NULL
                      REFERENCES payments(id),

  reason_code         varchar(80) NOT NULL,
  external_reference  varchar(160),

  opened_at           timestamptz NOT NULL,
  resolved_at         timestamptz,
  resolution          varchar(80),
  evidence_hash       char(64),

  CONSTRAINT ck_reconciliation_resolution
    CHECK (
      (resolved_at IS NULL AND resolution IS NULL)
      OR
      (resolved_at IS NOT NULL AND resolution IS NOT NULL)
    )

);

CREATE UNIQUE INDEX uq_reconciliation_open_payment
  ON reconciliation_cases(payment_id)
  WHERE resolved_at IS NULL;

-- -----------------------------------------------------------------------------
-- 7. AUDITORIA APPEND-ONLY
-- -----------------------------------------------------------------------------

CREATE TABLE audit_events (

  sequence        bigserial PRIMARY KEY,
  event_type      varchar(80) NOT NULL,
  actor_id        varchar(160) NOT NULL,
  subject_id      varchar(160) NOT NULL,
  payload         jsonb NOT NULL,

  occurred_at     timestamptz NOT NULL,
  previous_hash   char(64) NOT NULL,
  event_hash      char(64) NOT NULL UNIQUE,

  CONSTRAINT ck_audit_previous_hash
    CHECK (previous_hash ~ '^[a-f0-9]{64}$'),
  CONSTRAINT ck_audit_event_hash
    CHECK (event_hash ~ '^[a-f0-9]{64}$')

);

CREATE OR REPLACE FUNCTION forbid_audit_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  RAISE EXCEPTION 'AUDIT_EVENT_IMMUTABLE';
END;
$$;

CREATE TRIGGER trg_audit_events_immutable
BEFORE UPDATE OR DELETE ON audit_events
FOR EACH ROW
EXECUTE FUNCTION forbid_audit_mutation();

COMMIT;

-- rollback em produção não apaga razão.
-- correção entra como nova migration.
-- histórico financeiro não volta para a gaveta.
