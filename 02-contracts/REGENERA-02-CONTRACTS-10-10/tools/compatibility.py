#!/usr/bin/env python3
import argparse
from common import load

def compare(old,new):
    breaks=[]
    if 'paths' in old and 'paths' in new:
        for path,item in old['paths'].items():
            if path not in new['paths']:
                breaks.append(f'path removed: {path}'); continue
            for method in item:
                if method.lower() in {'get','post','put','patch','delete'} and method not in new['paths'][path]:
                    breaks.append(f'operation removed: {method.upper()} {path}')
    if old.get('type')=='object' and new.get('type')=='object':
        old_req=set(old.get('required',[])); new_req=set(new.get('required',[]))
        added=new_req-old_req
        if added: breaks.append('required fields added: '+','.join(sorted(added)))
        for name,schema in old.get('properties',{}).items():
            if name not in new.get('properties',{}): breaks.append(f'property removed: {name}')
            elif schema.get('type')!=new['properties'][name].get('type'): breaks.append(f'type changed: {name}')
    return breaks

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('old'); ap.add_argument('new'); args=ap.parse_args()
    breaks=compare(load(args.old),load(args.new))
    if breaks:
        print('\n'.join(breaks)); raise SystemExit(1)
    print('compatibility: PASS')
if __name__=='__main__': main()
