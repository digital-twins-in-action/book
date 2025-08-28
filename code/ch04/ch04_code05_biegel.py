import stomp, json, time
from collections import deque
from datetime import datetime, timedelta

conn = stomp.Connection([("publicdatafeeds.networkrail.co.uk", 61618)])
window = deque()
count = 0


class Listener(stomp.ConnectionListener):
    def on_message(self, frame):
        global count, window

        cutoff = datetime.now() - timedelta(minutes=5)
        while window and window[0][0] < cutoff:
            window.popleft()

        for m in (
            json.loads(frame.body)
            if isinstance(json.loads(frame.body), list)
            else [json.loads(frame.body)]
        )[:5]:
            msg_type = m.get("header", {}).get("msg_type", "")
            body = m.get("body", {})

            if msg_type == "0003":  # Movement
                status = body.get("variation_status", "")
                train_id = body.get("train_id", "")
                print(f"🚂 {status} {train_id}")
                window.append((datetime.now(), train_id, status == "LATE"))

            count += 1
            if count % 25 == 0:  # Show stats
                late_count = sum(1 for _, _, is_late in window if is_late)
                on_time_rate = (
                    (len(window) - late_count) / len(window) * 100 if window else 100
                )
                print(
                    f"📊 5min window: {len(window)} movements, {on_time_rate:.1f}% on-time"
                )

        conn.ack(frame.headers["message-id"], frame.headers["subscription"])


conn.set_listener("", Listener())
conn.connect("YOUR_USERNAME", "YOUR_PASSWORD")
conn.subscribe("/topic/TRAIN_MVT_ALL_TOC", "id1", ack="client-individual")

print("🚂 Listening... (Ctrl+C to stop)")
try:
    while True:
        time.sleep(10)
except:
    conn.disconnect()
