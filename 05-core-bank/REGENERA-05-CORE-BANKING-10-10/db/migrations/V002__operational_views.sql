-- =============================================================================
-- CORE BANKING — VISÕES OPERACIONAIS
-- =============================================================================

-- leitura operacional precisa ser rápida.
-- mas nunca vira fonte paralela de verdade.

BEGIN;

SET search_path TO core_banking, public;

CREATE VIEW account_signed_balances AS
SELECT
  a.id AS account_id,
  a.currency,
  COALESCE(
    sum(
      CASE
        WHEN a.account_class IN ('ASSET', 'EXPENSE')
         AND p.side = 'DEBIT'
          THEN p.amount_minor

        WHEN a.account_class IN ('ASSET', 'EXPENSE')
         AND p.side = 'CREDIT'
          THEN -p.amount_minor

        WHEN a.account_class IN ('LIABILITY', 'EQUITY', 'REVENUE')
         AND p.side = 'CREDIT'
          THEN p.amount_minor

        ELSE -p.amount_minor
      END
    ),
    0
  )::bigint AS signed_balance_minor
FROM ledger_accounts a
LEFT JOIN ledger_postings p
  ON p.account_id = a.id
LEFT JOIN journal_entries e
  ON e.id = p.entry_id
 AND e.status = 'POSTED'
GROUP BY a.id, a.currency;

CREATE VIEW account_available_balances AS
SELECT
  b.account_id,
  b.currency,
  b.signed_balance_minor,
  b.signed_balance_minor
    - COALESCE(
        sum(h.amount_minor) FILTER (
          WHERE h.status = 'ACTIVE'
            AND h.expires_at > now()
        ),
        0
      )::bigint AS available_balance_minor
FROM account_signed_balances b
LEFT JOIN account_holds h
  ON h.account_id = b.account_id
GROUP BY
  b.account_id,
  b.currency,
  b.signed_balance_minor;

CREATE VIEW unresolved_financial_states AS
SELECT
  p.id AS payment_id,
  p.status,
  p.correlation_id,
  p.updated_at,
  r.id AS reconciliation_case_id,
  r.opened_at
FROM payments p
LEFT JOIN reconciliation_cases r
  ON r.payment_id = p.id
 AND r.resolved_at IS NULL
WHERE p.status IN ('UNKNOWN', 'RECONCILIATION_REQUIRED');

COMMIT;
