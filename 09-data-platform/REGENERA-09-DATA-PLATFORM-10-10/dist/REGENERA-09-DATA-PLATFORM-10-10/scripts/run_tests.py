from pathlib import Path
import io, os, sys, unittest, xml.etree.ElementTree as ET
from common import ROOT, EVIDENCE, FIXED_ISO, write_json

sys.path.insert(0, str(ROOT/'src'))
loader=unittest.TestLoader()
suite=loader.discover(str(ROOT/'tests'))
all_names=[]
def flatten(s):
    for item in s:
        if isinstance(item, unittest.TestSuite): flatten(item)
        else: all_names.append(item.id())
flatten(suite)
stream=io.StringIO()
runner=unittest.TextTestRunner(stream=stream, verbosity=2)
result=runner.run(suite)
records=[]
for test,trace in result.failures: records.append({"name":test.id(),"status":"FAIL","detail":trace})
for test,trace in result.errors: records.append({"name":test.id(),"status":"ERROR","detail":trace})
failed={r['name'] for r in records}
for name in sorted(all_names):
    if name not in failed: records.append({"name":name,"status":"PASS","detail":""})
records=sorted(records,key=lambda r:r['name'])
status='PASS' if result.wasSuccessful() else 'FAIL'
payload={"generated_at":FIXED_ISO,"status":status,"tests":len(records),"passed":sum(r['status']=='PASS' for r in records),"failed":sum(r['status']!='PASS' for r in records),"results":records}
write_json(EVIDENCE/'test-results.json',payload)
testsuite=ET.Element('testsuite',name='regenera-data-platform',tests=str(len(records)),failures=str(payload['failed']),errors='0',time='0')
for record in records:
    case=ET.SubElement(testsuite,'testcase',name=record['name'],time='0')
    if record['status']!='PASS': ET.SubElement(case,'failure',message=record['status']).text=record['detail']
ET.ElementTree(testsuite).write(EVIDENCE/'test-results.xml',encoding='utf-8',xml_declaration=True)
print(stream.getvalue(),end='')
print(f"tests: {status} ({payload['passed']}/{payload['tests']})")
for cache in ROOT.rglob('__pycache__'):
    import shutil; shutil.rmtree(cache,ignore_errors=True)
for pyc in ROOT.rglob('*.pyc'): pyc.unlink(missing_ok=True)
if not result.wasSuccessful(): sys.exit(1)
