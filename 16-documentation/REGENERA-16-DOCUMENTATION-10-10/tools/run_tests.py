from common import ROOT, EVIDENCE, json_dump
import unittest, json

def main():
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={
        'status':'PASS' if result.wasSuccessful() else 'FAIL',
        'tests_run':result.testsRun,
        'failures':len(result.failures),
        'errors':len(result.errors),
        'skipped':len(result.skipped),
    }
    json_dump(EVIDENCE/'TEST-RESULTS.json',report)
    print(json.dumps(report,ensure_ascii=False))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__': raise SystemExit(main())
