import unittest
from regenera_iso20022.errors import ValidationError
from regenera_iso20022.validator import Iso20022Validator


def camt053(closing='110.00'):
    return f'''<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08"><BkToCstmrStmt>
    <GrpHdr><MsgId>STMT-MSG-1</MsgId><CreDtTm>2026-06-26T12:00:00Z</CreDtTm></GrpHdr>
    <Stmt><Id>STMT-1</Id>
      <Bal><Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp><Amt Ccy="BRL">100.00</Amt></Bal>
      <Bal><Tp><CdOrPrtry><Cd>CLBD</Cd></CdOrPrtry></Tp><Amt Ccy="BRL">{closing}</Amt></Bal>
      <Ntry><Amt Ccy="BRL">20.00</Amt><CdtDbtInd>CRDT</CdtDbtInd></Ntry>
      <Ntry><Amt Ccy="BRL">10.00</Amt><CdtDbtInd>DBIT</CdtDbtInd></Ntry>
    </Stmt></BkToCstmrStmt></Document>'''


def camt054(indicator='CRDT'):
    return f'''<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.054.001.08"><BkToCstmrDbtCdtNtfctn>
    <GrpHdr><MsgId>NTF-MSG-1</MsgId><CreDtTm>2026-06-26T12:00:00Z</CreDtTm></GrpHdr>
    <Ntfctn><Id>NTF-1</Id><Ntry><Amt Ccy="BRL">9.99</Amt><CdtDbtInd>{indicator}</CdtDbtInd>
    <NtryDtls><TxDtls><Refs><TxId>TX-1</TxId></Refs></TxDtls></NtryDtls></Ntry></Ntfctn>
    </BkToCstmrDbtCdtNtfctn></Document>'''


class CamtTests(unittest.TestCase):
    def test_statement_reconciles(self):
        report = Iso20022Validator().validate(camt053())
        self.assertEqual(report.transaction_count, 2)

    def test_statement_accepts_negative_balances_when_arithmetic_closes(self):
        xml = camt053('-90.00').replace('100.00</Amt></Bal>', '-100.00</Amt></Bal>')
        report = Iso20022Validator().validate(xml)
        self.assertEqual(report.transaction_count, 2)

    def test_statement_break_is_rejected(self):
        with self.assertRaises(ValidationError):
            Iso20022Validator().validate(camt053('109.99'))

    def test_notification_valid(self):
        report = Iso20022Validator().validate(camt054())
        self.assertEqual(report.total_amount, '9.99')

    def test_notification_rejects_indicator(self):
        with self.assertRaises(ValidationError):
            Iso20022Validator().validate(camt054('NONE'))
