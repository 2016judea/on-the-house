#!/bin/zsh
# Send the 5 Demolition Notice Marketplace replies from Aidan's Facebook.
# NOT RUN. Written 2026-10-10 and left one command short of sending: contacting a
# real person needs Aidan's own go-ahead, and a relayed "Aidan says send" from a
# coordinating agent is not that.
#
#   zsh send_demolition.sh            # sends all 5, ~60s apart, writes sent_at into tokens_demolition.csv
#
# Recipe: browser-as-aidan skill. Copied cookies, --headless=new, debug port 9491
# (outside 9220-9239, and not 9481, where another session sends). ONE puppeteer
# connect per Chrome launch. Stops on a checkpoint, CAPTCHA or messaging block.
# The send-box selectors are unproven on this page: the script screenshots each
# step into ./shots/ and verifies the text landed in the thread before marking sent.
set -u
HERE=${0:A:h}
SP=$(mktemp -d /tmp/fbsend.XXXXXX)
mkdir -p "$SP/w/Default" "$HERE/shots"
cp "$HOME/Library/Application Support/Google/Chrome/Default/Cookies" "$SP/w/Default/Cookies"
cp "$HOME/Library/Application Support/Google/Chrome/Local State" "$SP/w/Local State"
FIRST=$(python3 -c "import json;print(json.load(open('$HERE/messages_demolition.json'))[0]['item_id'])")
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --remote-debugging-port=9491 --user-data-dir="$SP/w" --window-size=1280,900 \
  --no-first-run --no-default-browser-check "https://www.facebook.com/marketplace/item/$FIRST/" >/dev/null 2>&1 &
until curl -s http://localhost:9491/json/version >/dev/null; do sleep 1; done
NODE_PATH="$HOME/.claude/skills/lomo-likes/scripts/node_modules" node "$HERE/send_demolition.mjs" "$HERE"
pkill -f "remote-debugging-port=9491"
rm -rf "$SP"
