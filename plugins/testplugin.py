from typing import Tuple
import pandas as pd
import numpy as np

def defineTest():
    return MyTest()

class MyTest:
    testName = "Front Left Normal Distribution"
    entries: Tuple[str] = ('/swerve/Front Left/drive/position',)

    def runTest(df: pd.DataFrame) -> Tuple[int, str]:
        return
