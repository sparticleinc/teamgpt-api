

#!/bin/sh
aerich upgrade
uvicorn teamgpt.app:app --host 127.0.0.1 --no-access-log --port 8000 --workers 2 --reload