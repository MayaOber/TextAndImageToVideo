import requests
from requests import Response
import json
import os
import argparse
from typing import Literal
import time
import sys
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_URL = ' https://mercury.dev.dream-ai.com/api'

load_dotenv()

api_key = os.getenv("HEDRA_API_KEY")

headers={'X-API-KEY': api_key}

response = requests.get(
    f"{BASE_URL}/v1/voices",
    headers=headers
)

print(json.dumps(response.json(), indent=4, sort_keys=True))