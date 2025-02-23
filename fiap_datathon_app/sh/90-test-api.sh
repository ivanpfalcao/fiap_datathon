
URL="http://127.0.0.1:8000"
API_KEY="your_default_api_token"


curl -X POST "${URL}/recommendation/" --header "Authorization: Bearer ${API_KEY}" \
--header "Content-Type: application/json" \
--data '{ "viewed_news": [ "c8aab885-433d-4e46-8066-479f40ba7fb2", "68d2039c-c9aa-456c-ac33-9b2e8677fba7", "13e423ce-1d69-4c78-bc18-e8c8f7271964"], "init_time": "2022-12-31T00:00:00", "end_time": "2026-12-31T00:00:00" }'