"""Daily opt-in distribution. Endpoints must be HTTPS and explicitly authorized.
DISTRIBUTION_ENDPOINTS is a JSON array of approved HTTPS POST URLs.
No automatic applications, email blasts, or platform scraping.
"""
import datetime as dt
import json
import os
import urllib.request
import urllib.parse

with open('candidate.json', encoding='utf-8') as f:
    candidate = json.load(f)

endpoints = json.loads(os.environ.get('DISTRIBUTION_ENDPOINTS') or '[]')
if not isinstance(endpoints, list):
    raise ValueError('DISTRIBUTION_ENDPOINTS must be a JSON array')

payload = {
    'candidate': candidate['name'],
    'target_roles': candidate['target_roles'],
    'location_preferences': candidate['location_preferences'],
    'verified_skills': candidate['verified_skills'],
    'profile_url': candidate['profile_url'],
    'status': 'AVAILABLE_FOR_CONSIDERATION'
}
results = []
for endpoint in endpoints:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        results.append({'destination': 'invalid endpoint', 'status': 'SKIPPED'})
        continue
    headers = {'Content-Type': 'application/json'}
    token = os.environ.get('DISTRIBUTION_TOKEN', '')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            results.append({'destination_host': parsed.hostname, 'status': response.status})
    except Exception as exc:
        results.append({'destination_host': parsed.hostname, 'status': 'FAILED', 'error_type': type(exc).__name__})

report = {'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'destinations_configured': len(endpoints), 'results': results}
with open('distribution-report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
