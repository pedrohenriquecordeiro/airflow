# get default password
export REDIS_PASSWORD=$(kubectl get secret --namespace redis redis -o jsonpath="{.data.redis-password}" | base64 -d)

# type in terminal
# > redis-cli

AUTH LaY2khMDOX # temporary password

KEYS *

SET red '2023-10-01 00:00:00'
GET latest_timestamp

SET latest_timestamp '2025-10-01 00:00:00'
GET latest_timestamp
