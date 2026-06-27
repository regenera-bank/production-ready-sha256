import test from 'node:test';
import assert from 'node:assert/strict';
import { assertCorporateIdentity, assertGrant, ApprovalService } from '../packages/operations-bff/src/index.mjs';
import { AuditChain } from '../packages/shared/src/audit-chain.mjs';

test('operations exige identidade corporativa', () => assert.throws(() => assertCorporateIdentity({ source: 'PUBLIC_IDP', mfa: true, actorId: 'a' }), /CORPORATE_IDENTITY_REQUIRED/));
test('operations exige mfa', () => assert.throws(() => assertCorporateIdentity({ source: 'CORPORATE_IDP', mfa: false, actorId: 'a' }), /CORPORATE_MFA_REQUIRED/));
test('privilégio vencido é bloqueado', () => assert.throws(() => assertGrant({ approved: true, expiresAt: '2020-01-01', permissions: ['x'] }, Date.now()), /PRIVILEGE_EXPIRED/));
test('autoaprovação é bloqueada', () => assert.throws(() => new ApprovalService().approve({ requestId: 'r', makerId: 'u1', checkerId: 'u1', permission: 'PIX_CANCEL', evidenceRef: 'INC-1234' }), /SELF_APPROVAL_FORBIDDEN/));
test('aprovação exige evidência', () => assert.throws(() => new ApprovalService().approve({ requestId: 'r', makerId: 'u1', checkerId: 'u2', permission: 'PIX_CANCEL', evidenceRef: '' }), /EVIDENCE_REQUIRED/));
test('aprovação entra em trilha verificável', () => {
  const chain = new AuditChain();
  new ApprovalService(chain).approve({ requestId: 'r', makerId: 'u1', checkerId: 'u2', permission: 'PIX_CANCEL', evidenceRef: 'INC-1234' });
  assert.equal(AuditChain.verify(chain.entries()), true);
});
