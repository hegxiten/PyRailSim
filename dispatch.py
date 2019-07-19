#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(
    'D:\\Users\\Hegxiten\\workspace\\Rutgers_Railway_security_research\\OOD_Train'
)
import random
import numpy as np
from datetime import datetime, timedelta
from collections.abc import MutableSequence
from infrastructure import Track, BigBlock
from signaling import AutoSignal, HomeSignal, AutoPoint, ControlPoint

class DispatchStage():
    def __init__(self):
        pass
    
    @property
    def curr_conflicts(self):
        pass
    
    @property
    def 