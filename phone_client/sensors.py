import math
import random
import time

#simulate accelerometer data 

def read_accelerometer():

    t = time.time()
    freq = 2.0  # ~2 steps per second
    walking_wave = math.sin(2 * math.pi * freq * t)

    base = 9.8   # gravity
    amp = 1.5    # movement amplitude

    mag = base + amp * walking_wave + random.uniform(-0.3, 0.3)

    ax = mag * 0.6 + random.uniform(-0.2, 0.2)
    ay = mag * 0.3 + random.uniform(-0.2, 0.2)
    az = mag * 0.1 + random.uniform(-0.2, 0.2)

    return ax, ay, az