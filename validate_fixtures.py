#!/usr/bin/env python3
from pathlib import Path
import json, sys
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parent
SCHEMAS=ROOT/'schemas'
VALID=ROOT/'fixtures'/'valid'
INVALID=ROOT/'fixtures'/'invalid'

schemas={}
registry=Registry()
for p in SCHEMAS.glob('*.schema.json'):
    data=json.loads(p.read_text(encoding='utf-8'))
    schemas[p.name]=data
    registry=registry.with_resource(data['$id'], Resource.from_contents(data))

mapping={
 'frontier':'frontier.schema.json','application':'application.schema.json','subscriber':'subscriber.schema.json',
 'agent-access':'agent-access.schema.json','subscription':'subscription.schema.json','observation-authorization':'observation-authorization.schema.json',
 'source-registration':'source-registration.schema.json','event':'event.schema.json','signal':'signal.schema.json','coordinate-payload':'coordinate-payload.schema.json',
 'reducer-policy':'reducer-policy.schema.json','delivery':'delivery.schema.json','replay-cursor':'replay-cursor.schema.json',
 'agent-stream-request':'agent-stream-request.schema.json','journal-record':'journal-record.schema.json','coordinate':'coordinate-payload.schema.json','observation-authorization':'observation-authorization.schema.json'
}

def schema_for(path):
    stem=path.name.split('.')[0]
    if stem in mapping: return schemas[mapping[stem]]
    raise KeyError(f'No schema mapping for {path.name}')

def check(path, should_pass):
    obj=json.loads(path.read_text(encoding='utf-8'))
    v=Draft202012Validator(schema_for(path), registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors=list(v.iter_errors(obj))
    ok=(not errors) if should_pass else bool(errors)
    if not ok:
        print(f'FAIL {path.relative_to(ROOT)}')
        if errors:
            for e in errors[:5]: print('  -', e.message)
        else: print('  - invalid fixture unexpectedly validated')
    else:
        print(f'PASS {path.relative_to(ROOT)}')
    return ok

all_ok=True
for p in sorted(VALID.glob('*.json')): all_ok &= check(p, True)
for p in sorted(INVALID.glob('*.json')): all_ok &= check(p, False)
print('OK' if all_ok else 'FAILED')
sys.exit(0 if all_ok else 1)
