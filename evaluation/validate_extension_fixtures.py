#!/usr/bin/env python3
from pathlib import Path
import json, sys
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parent
schemas={}
registry=Registry()
for p in (ROOT/'schemas').glob('*.schema.json'):
    d=json.loads(p.read_text())
    schemas[p.name]=d
    registry=registry.with_resource(d['$id'],Resource.from_contents(d))

mapping={
 'evaluation-profile':'evaluation-profile.schema.json',
 'scenario':'scenario.schema.json',
 'trial-result':'trial-result.schema.json',
 'run-manifest':'run-manifest.schema.json',
 'summary':'summary.schema.json',
}
def schema_for(p): return schemas[mapping[p.name.split('.')[0]]]
def check(p,valid):
    d=json.loads(p.read_text())
    errs=list(Draft202012Validator(schema_for(p),registry=registry,format_checker=Draft202012Validator.FORMAT_CHECKER).iter_errors(d))
    ok=(not errs) if valid else bool(errs)
    if not ok:
        print('FAIL',p.relative_to(ROOT),errs[0].message if errs else 'unexpectedly valid')
    return ok
ok=True
for p in sorted((ROOT/'fixtures'/'valid').glob('*.json')): ok &= check(p,True)
for p in sorted((ROOT/'fixtures'/'invalid').glob('*.json')): ok &= check(p,False)
print('OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
