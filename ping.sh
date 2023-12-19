#!/bin/bash
set -e

MESSAGE="Ping was failed!"

send_telegram() {
	curl -X POST \
            -H 'Content-Type: application/json' \
            -d '{"parse_mode": "markdown", "chat_id": "'"$TELEGRAM_CHAT_ID"'", "text": "'"$PROJECT_NAME"': '"$MESSAGE"'"}' \
            "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage"

}

send_gotify() {
	curl "$GOTIFY_HOST/message?token=$GOTIFY_APP_TOKEN" \
		-F "title=$PROJECT_NAME" \
		-F "message=$MESSAGE" \
		-F "priority=5"

}

echo "Try to check $PING_URL"
status_code=$(curl --write-out %{http_code} --silent --output /dev/null $PING_URL)

if [[ "$status_code" -ne 200 ]] ; then
    echo "Error!"
	send_telegram
	send_gotify
else
	echo "All is good!"
fi