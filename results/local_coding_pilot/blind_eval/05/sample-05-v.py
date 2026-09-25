import os
import sys
import glob
import json
import re
import time
from datetime import datetime, timezone

def parse_timestamp(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None

def now_utc():
    return datetime.now(timezone.utc)

def get_file_time(file_path):
    filename = os.path.basename(file_path)
    match = re.match(r'^MSG-(\d{8})-(\d{4})-(ALL|bm-[a-z0-9]+)-(.+)\.md$', filename)
    if not match:
        return None, -1.0
    try:
        date_part = match.group(1)
        time_part = match.group(2)
        dt = datetime.strptime(f"{date_part}-{time_part}", "%Y%m%d-%H%M")
        dt = dt.replace(tzinfo=timezone.utc)
        return filename, dt
    except ValueError:
        return filename, -1.0

def process_inbox(inbox_dir, machines_dir):
    inbox_files = glob.glob(os.path.join(inbox_dir, "MSG-*.md"))
    heartbeat_files = glob.glob(os.path.join(machines_dir, "*.json")) if os.path.exists(machines_dir) else []

    # Load heartbeats
    heartbeats = {}
    for hb_file in heartbeat_files:
        try:
            with open(hb_file, 'r') as f:
                data = json.load(f)
                machine_id = os.path.basename(hb_file).replace('.json', '')
                last_seen = data.get('last_seen')
                if last_seen:
                    ts = parse_timestamp(last_seen)
                    if ts:
                        heartbeats[machine_id] = ts
        except Exception:
            pass

    total = len(inbox_files)
    name_fail = 0
    unprocessed = 0
    stalled1h = 0
    stranded = 0
    max_age_h = -1.0
    rows = []

    now = now_utc()

    for file_path in inbox_files:
        filename, filed_at = get_file_time(file_path)
        if filed_at == -1.0:
            name_fail += 1
            continue

        age_h = (now - filed_at).total_seconds() / 3600.0
        if age_h < 0:
            age_h = -1.0

        recipient = filename.split('-')[3]
        liveness_min = float('inf')
        is_fresh = False
        is_unknown = True

        if recipient == 'ALL':
            if heartbeats:
                latest = max(heartbeats.values())
                liveness_min = (now - latest).total_seconds() / 60.0
                is_fresh = liveness_min <= 20
                is_unknown = False
        else:
            if recipient in heartbeats:
                last_seen = heartbeats[recipient]
                liveness_min = (now - last_seen).total_seconds() / 60.0
                is_fresh = liveness_min <= 20
                is_unknown = False

        eta_class = 'clock_anomaly'
        if age_h >= 0:
            if is_fresh:
                eta_class = 'due_next_pull'
            elif is_unknown or liveness_min > 20:
                eta_class = 'stranded'
        else:
            eta_class = 'clock_anomaly'

        unprocessed += 1
        if age_h >= 0:
            if age_h > 1.0:
                stalled1h += 1
            if eta_class == 'stranded':
                stranded += 1
            if max_age_h < 0 or age_h > max_age_h:
                max_age_h = age_h

        rows.append((filename, recipient, age_h, eta_class))

    # Sort rows: by age_h descending, then filename ascending
    rows.sort(key=lambda x: (-x[2], x[0]))

    # Print summary line
    print(f"INBOX total={total} name_fail={name_fail} unprocessed={unprocessed} stalled1h={stalled1h} stranded={stranded} max_age_h={max_age_h:.1f}")

    for filename, recipient, age_h, eta_class in rows:
        print(f"MSG {filename} to={recipient} age_h={age_h:.1f} eta={eta_class}")

    return stalled1h

def selftest():
    # Mock data
    test_cases = [
        # (filename, heartbeats, now, expected_result)
        (
            "MSG-20240501-1200-bm-abc-topic.md",
            {"bm-abc": "2024-05-01T12:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("due_next_pull", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-def-topic.md",
            {"bm-def": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-ALL-topic.md",
            {"bm-abc": "2024-05-01T12:00:00", "bm-def": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("due_next_pull", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-ghi-topic.md",
            {"bm-ghi": None},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-jkl-topic.md",
            {},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-mno-topic.md",
            {"bm-mno": "2024-05-01T12:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("due_next_pull", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-pqr-topic.md",
            {"bm-pqr": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-stu-topic.md",
            {"bm-stu": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-vwx-topic.md",
            {"bm-vwx": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-yz-topic.md",
            {"bm-yz": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-abc-topic.md",
            {"bm-abc": "2024-05-01T12:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("due_next_pull", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-def-topic.md",
            {"bm-def": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-ghi-topic.md",
            {"bm-ghi": None},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-jkl-topic.md",
            {},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-mno-topic.md",
            {"bm-mno": "2024-05-01T12:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("due_next_pull", 0.167)
        ),
        (
            "MSG-20240501-1200-bm-pqr-topic.md",
            {"bm-pqr": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-stu-topic.md",
            {"bm-stu": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-vwx-topic.md",
            {"bm-vwx": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
        (
            "MSG-20240501-1200-bm-yz-topic.md",
            {"bm-yz": "2024-05-01T11:00:00"},
            datetime(2024, 5, 1, 12, 10, tzinfo=timezone.utc),
            ("stranded", 1.0)
        ),
    ]

    # Simulate processing
    total = len(test_cases)
    name_fail = 0
    unprocessed = 0
    stalled1h = 0
    stranded = 0
    max_age_h = -1.0

    rows = []

    for filename, heartbeats, now, expected in test_cases:
        # Simulate file parsing
        match = re.match(r'^MSG-(\d{8})-(\d{4})-(ALL|bm-[a-z0-9]+)-(.+)\.md$', filename)
        if not match:
            name_fail += 1
            continue

        try:
            date_part = match.group(1)
            time_part = match.group(2)
            dt = datetime.strptime(f"{date_part}-{time_part}", "%Y%m%d-%H%M")
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            name_fail += 1
            continue

        age_h = (now - dt).total_seconds() / 3600.0
        if age_h < 0:
            age_h = -1.0

        recipient = match.group(3)

        # Simulate liveness logic
        liveness_min = float('inf')
        is_fresh = False
        is_unknown = True

        if recipient == 'ALL':
            if heartbeats:
                latest = max([parse_timestamp(ts) for ts in heartbeats.values() if ts])
                if latest:
                    liveness_min = (now - latest).total_seconds() / 60.0
                    is_fresh = liveness_min <= 20
                    is_unknown = False
        else:
            if recipient in heartbeats and heartbeats[recipient]:
                last_seen = parse_timestamp(heartbeats[recipient])
                if last_seen:
                    liveness_min = (now - last_seen).total_seconds() / 60.0
                    is_fresh = liveness_min <= 20
                    is_unknown = False

        eta_class = 'clock_anomaly'
        if age_h >= 0:
            if is_fresh:
                eta_class = 'due_next_pull'
            elif is_unknown or liveness_min > 20:
                eta_class = 'stranded'
        else:
            eta_class = 'clock_anomaly'

        unprocessed += 1
        if age_h >= 0:
            if age_h > 1.0:
                stalled1h += 1
            if eta_class == 'stranded':
                stranded += 1
            if max_age_h < 0 or age_h > max_age_h:
                max_age_h = age_h

        rows.append((filename, recipient, age_h, eta_class))

    # Sort rows: by age_h descending, then filename ascending
    rows.sort(key=lambda x: (-x[2], x[0]))

    # Print summary line
    print(f"INBOX total={total} name_fail={name_fail} unprocessed={unprocessed} stalled1h={stalled1h} stranded={stranded} max_age_h={max_age_h:.1f}")

    for filename, recipient, age_h, eta_class in rows:
        print(f"MSG {filename} to={recipient} age_h={age_h:.1f} eta={eta_class}")

    # Validate results
    expected_total = 18
    expected_name_fail = 0
    expected_unprocessed = 18
    expected_stalled1h = 0
    expected_stranded = 12
    expected_max_age_h = 0.167

    if (total == expected_total and name_fail == expected_name_fail and
        unprocessed == expected_unprocessed and stalled1h == expected_stalled1h and
        stranded == expected_stranded and abs(max_age_h - expected_max_age_h) < 0.01):
        print("ALL PASS")
        return 0
    else:
        print("FAILED")
        return 1

def main():
    if len(sys.argv) == 1:
        print("Usage: python inbox_aging.py [inbox_dir] [machines_dir]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        sys.exit(selftest())
    else:
        inbox_dir = sys.argv[1] if len(sys.argv) > 1 else "fleet/inbox"
        machines_dir = sys.argv[2] if len(sys.argv) > 2 else "fleet/machines"

        if not os.path.exists(inbox_dir):
            print(f"Error: inbox directory {inbox_dir} does not exist", file=sys.stderr)
            sys.exit(2)

        try:
            stalled1h = process_inbox(inbox_dir, machines_dir)
            sys.exit(1 if stalled1h > 0 else 0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)

if __name__ == "__main__":
    main()
