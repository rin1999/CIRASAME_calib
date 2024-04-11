import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re
import glob
import numpy as np


class Data_reader:

    def __init__(self, ch: int, file_path: str) -> None:
        self.ch = ch
        self.file_path = file_path
        