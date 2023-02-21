# Sample Distributed Field Bus Application
## Setup

```bash
pip install virtualenv
virtualenv -p python3 .env
source .env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Config
point main.py to the correct simulation and message bus configs

```python
GOSS_CONFIG = "config/pnnl.goss.gridappsd.cfg"
SIM_CONFIG = "config/ieee123.json"
BUS_CONFIG = "config/system_message_bus.yml"
```

make sure the gridappsd container is running the matching feeder, there is an assert to compare the config files. If there is a missmatch update the goss config and copy it into the docker container and rerun. 

```bash
docker cp config/pnnl.goss.gridappsd.cfg  gridappsd:/gridappsd/conf/pnnl.goss.gridappsd.cfg
```

## Run
run main.py from the termanal in the main directory.

```bash
python main.py
```