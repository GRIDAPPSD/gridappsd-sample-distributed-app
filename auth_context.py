import os

gridappsd_user = os.environ.get("GRIDAPPSD_USER", "app_user")
gridappsd_password = os.environ.get("GRIDAPPSD_PASSWORD", "1234App")
gridappsd_address = os.environ.get("GRIDAPPSD_ADDRESS", "gridappsd")
gridappsd_port = os.environ.get("GRIDAPPSD_PORT", "61613")

os.environ['GRIDAPPSD_APPLICATION_ID'] = 'dist-sample-app'
os.environ['GRIDAPPSD_USER'] = gridappsd_user
os.environ['GRIDAPPSD_PASSWORD'] = gridappsd_password
os.environ['GRIDAPPSD_ADDRESS'] = gridappsd_address
os.environ['GRIDAPPSD_PORT'] = gridappsd_port