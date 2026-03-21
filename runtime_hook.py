import sys
import os
from pathlib import Path

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = Path(__file__).parent

sys.path.insert(0, application_path)

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
