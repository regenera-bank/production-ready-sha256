import unittest

from regenera_iso20022.errors import ValidationError
from regenera_iso20022.validator import Iso20022Validator


def message(status='ACSC', include_reason=False):
    reason = '<StsRsnInf><Rsn><Cd>AC01</Cd></Rsn></StsRsnInf>' if include_reason else ''
    return f'''<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10">
      <FIToFIPmtStsRpt><GrpHdr><MsgId>STS-1</MsgId><CreDtTm>2026-06-26T12:00:00Z</CreDtTm></GrpHdr>
      <OrgnlGrpInfAndSts><OrgnlMsgId>MSG-1</OrgnlMsgId><GrpSts>{status}</GrpSts>{reason}</OrgnlGrpInfAndSts>
      <TxInfAndSts><OrgnlTxId>TX-1</OrgnlTxId><TxSts>{status}</TxSts></TxInfAndSts>
      </FIToFIPmtStsRpt></Document>'''


class Pacs002Tests(unittest.TestCase):
    def test_accepts_settled(self):
        report = Iso20022Validator().validate(message())
        self.assertEqual(report.transaction_count, 1)

    def test_reject_requires_reason(self):
        with self.assertRaises(ValidationError):
            Iso20022Validator().validate(message('RJCT'))

    def test_reject_with_reason_is_valid(self):
        report = Iso20022Validator().validate(message('RJCT', True))
        self.assertEqual(report.message_type, 'pacs.002.001.10')

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            Iso20022Validator().validate(message('DONE'))
