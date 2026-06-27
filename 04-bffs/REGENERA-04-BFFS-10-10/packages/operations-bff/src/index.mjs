import { assert } from '../../shared/src/errors.mjs';
import { AuditChain } from '../../shared/src/audit-chain.mjs';

export function assertCorporateIdentity(identity) {
  assert(identity?.source === 'CORPORATE_IDP', 'CORPORATE_IDENTITY_REQUIRED', 401);
  assert(identity.mfa === true, 'CORPORATE_MFA_REQUIRED', 403);
  assert(typeof identity.actorId === 'string' && identity.actorId.length > 0, 'ACTOR_REQUIRED', 401);
}

export function assertGrant(grant, now = Date.now()) {
  assert(grant?.approved === true, 'PRIVILEGE_NOT_APPROVED', 403);
  assert(new Date(grant.expiresAt).getTime() > now, 'PRIVILEGE_EXPIRED', 403);
  assert(Array.isArray(grant.permissions) && grant.permissions.length > 0, 'PRIVILEGE_EMPTY', 403);
}

export class ApprovalService {
  constructor(chain = new AuditChain()) {
    this.chain = chain;
  }

  approve({ requestId, makerId, checkerId, permission, evidenceRef }) {
    assert(makerId !== checkerId, 'SELF_APPROVAL_FORBIDDEN', 403);
    assert(typeof evidenceRef === 'string' && evidenceRef.length >= 8, 'EVIDENCE_REQUIRED', 422);
    return this.chain.append({ requestId, makerId, checkerId, permission, evidenceRef, outcome: 'APPROVED' });
  }
}
