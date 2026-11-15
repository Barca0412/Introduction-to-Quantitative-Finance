"""Fail deployment when public pages or its exact data snapshot differ."""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlencode, urlsplit

root = Path(sys.argv[1])
origin = sys.argv[2].rstrip('/')
expected = (root / 'arxiv-data/manifest.json').read_bytes()
digest = hashlib.sha256(expected).hexdigest()
paths = ['/', '/tutorials/', '/resources/', '/library/', '/contact', '/arxiv/',
         '/arxiv/papers', '/arxiv/trends', '/arxiv/people', '/arxiv/about']
for kind in ['institution', 'author']:
    examples = sorted((root / 'arxiv-data/agg' / kind).glob('*.json'))
    if examples: paths.append(f'/arxiv/{kind}?id={examples[0].stem}')
for path in paths:
    request = urllib.request.Request(origin + path, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200: raise SystemExit(f'{path}: HTTP {response.status}')
        if 'text/html' not in response.headers.get('Content-Type', ''): raise SystemExit(f'{path}: expected HTML')
        remote_html = response.read()
    pathname = urlsplit(path).path.lstrip('/')
    local_html = root / (pathname + 'index.html' if path.endswith('/') else pathname + '.html')
    if hashlib.sha256(remote_html).digest() != hashlib.sha256(local_html.read_bytes()).digest():
        raise SystemExit(f'{path}: published page differs from this build')
    print(f'OK {path}')
with urllib.request.urlopen(origin + '/arxiv-data/manifest.json?' + urlencode({'verify': digest}), timeout=30) as response:
    actual = response.read()
if hashlib.sha256(actual).hexdigest() != digest:
    raise SystemExit('Published Radar manifest differs from this build')
print(f'Exact manifest verified; data through {json.loads(actual)["latest_published_date"]}')
build_info = (root / 'build-info.json').read_bytes()
with urllib.request.urlopen(origin + '/build-info.json?' + urlencode({'verify': digest}), timeout=30) as response:
    published_info = response.read()
if published_info != build_info:
    raise SystemExit('Published build identity differs from this build')
print(f'Build identity verified: {json.loads(build_info)["commit"]}')
