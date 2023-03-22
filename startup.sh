

#!/bin/sh
aerich upgrade
uvicorn teamgpt.app:app --host 0.0.0.0 --no-access-log --port 8001 --workers 2 --reload