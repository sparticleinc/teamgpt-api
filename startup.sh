

#!/bin/sh
aerich upgrade
uvicorn teamgpt.app:app --host 0.0.0.0 --no-access-log --port 8000 --workers 2 --reload