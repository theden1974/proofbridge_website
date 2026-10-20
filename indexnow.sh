#!/bin/sh
# Tell Bing / IndexNow engines that proofbridge.nl changed. Run after every push (from your Mac).
curl -s -H "Content-Type: application/json; charset=utf-8" https://api.indexnow.org/indexnow -d '{
  "host": "proofbridge.nl",
  "key": "3b4147ea6090327fcb6043441e64d8cc",
  "keyLocation": "https://proofbridge.nl/3b4147ea6090327fcb6043441e64d8cc.txt",
  "urlList": ["https://proofbridge.nl/", "https://proofbridge.nl/llms.txt", "https://proofbridge.nl/offer.json", "https://proofbridge.nl/index.md", "https://proofbridge.nl/backlog.json"]
}' -w "IndexNow HTTP %{http_code}\n"
