import urllib.request
import json

url = 'http://localhost:8000/api/failure-chain/missions'
req = urllib.request.urlopen(url)
print('HTTP status:', req.status)
data = json.loads(req.read().decode())
print(f'Total missions with chains: {len(data)}')
for m in data:
    print(f'Incident #{m["incident_id"]} | {m["space_agency"]} - {m["mission_name"]} | Subsystem: {m["subsystem"]} | Events: {m["event_count"]}')

# Test retrieving the chain for the last mission (Starliner)
starliner_incident = data[-1]["incident_id"]
url_chain = f'http://localhost:8000/api/failure-chain/{starliner_incident}'
req_chain = urllib.request.urlopen(url_chain)
chain_data = json.loads(req_chain.read().decode())
print('=' * 60)
print('Retrieved Chain for:', chain_data['mission_name'])
print('Document ID:', chain_data.get('document_id'))
print('Root cause:', chain_data['root_cause'])
print('Events count:', len(chain_data['events']))
for ev in chain_data['events']:
    print(f'  Node #{ev["event_order"]}: [{ev["event_type"]}] {ev["event_title"]} (Page {ev["source_page"]})')
print('=' * 60)
