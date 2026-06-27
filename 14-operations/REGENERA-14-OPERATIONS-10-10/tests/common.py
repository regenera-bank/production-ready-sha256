from datetime import datetime, timezone, timedelta
D="a"*64
D2="b"*64
NOW=datetime(2026,6,26,12,0,tzinfo=timezone.utc)
LATER=NOW+timedelta(hours=1)
