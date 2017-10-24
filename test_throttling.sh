#!/usr/bin/env bash


auth_token_obj=$(curl -H "Content-Type: application/json" \
        -X POST \
        -d '{"username": "Andrej","password": "andrej0410"}' \
        146.185.174.207/auth)

auth_token=$(echo "$auth_token_obj" | python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')


for i in {0000000001..0000000015}; do
    curl -H "Content-Type: application/json" \
            -X POST \
            -d '{"contact_no": '"$RANDOM"'}' \
            146.185.174.207/call_me/"$i"
done


for i in {0000000001..0000000015}; do
    curl -H "Content-Type: application/json" \
            -H "Authorization: JWT $auth_token" \
            -X DELETE \
            146.185.174.207/call_me/"$i"
done