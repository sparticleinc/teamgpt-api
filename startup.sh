

#!/bin/sh
aerich upgrade
uvicorn teamgpt.app:app --host 0.0.0.0 --port 8000  --workers 2 --reload --no-access-log