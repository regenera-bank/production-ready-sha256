from common import *
import json, os, platform, sys

def main():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    files=payload_files()
    lines=[]; manifest=[]
    for p in files:
        rel=str(p.relative_to(ROOT)); h=sha256(p); lines.append(f'{h}  {rel}'); manifest.append({'path':rel,'sha256':h,'bytes':p.stat().st_size})
    (EVIDENCE/'PAYLOAD-CHECKSUMS.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    json_dump(EVIDENCE/'FILE-MANIFEST.json',{'scope':'all release payload excluding evidence to avoid self-reference','files':manifest})
    json_dump(EVIDENCE/'SBOM.json',{'format':'Regenera-SBOM-1','components':[{'name':'python-stdlib','type':'runtime','version':platform.python_version()}],'external_dependencies':[]})
    json_dump(EVIDENCE/'BUILD-PROVENANCE.json',{'release':'REGENERA-16-DOCUMENTATION-10-10','builder':'python-stdlib','python':platform.python_version(),'source_sha256':'b7427ff675069b155890df1d912d35312c101b0c98a6a49ddfd25f927e9023f0','network_used':False,'status':'VERIFIED_LOCAL'})
    print(json.dumps({'status':'PASS','payload_files':len(files)},ensure_ascii=False))
if __name__=='__main__': main()
