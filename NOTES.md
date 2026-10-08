== curl ==
# GET  /api/subscribe?token=1&sub_type=ss
# POST /api/traffic -H "X-API-Token: dev-api-token"  {"node_id":1,"users":[{"id":1,"upload":1024,"download":2048}]}
# POST /api/admin/users  {"username":"bob","rate_up":5,"rate_down":5,"traffic":10737418240}
# GET  /api/admin/analytics
# CLI: moess stats

== session plan ==
# Session 1: models + seed + subscribe + traffic sync (port FluxGate) → tests
# Session 2: admin CRUD + rate limits + analytics → tests
# Session 3: web templates (FluxGate dark UI) + bot + cli → screenshots → README → CI/Docker/Pages → tag
