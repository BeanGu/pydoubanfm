#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from doubanfm.client.base import Protocol
from doubanfm.utils import run_client
run_client(Protocol())
