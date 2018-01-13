import brains
import numpy as np
import time
import sys

# Experiment preparation
# =============CONSTANTS============= #
'''
The Constants for generation of sound signals for experiment
'''
N_SIGNALS = 40
F0 = 310
F1 = 500
SAMPLE_LEN = .15
INTERVAL = 0.85
N_REPEAT = 30
BREAK = 0

## Defining the sounds
S0 = brains.gen_sound(F0,SAMPLE_LEN)
S1 = brains.gen_sound(F1,SAMPLE_LEN)

high_low_order = (brains.gen_order(N_REPEAT, N_REPEAT//2))

# Running the experiment
for index, rep in enumerate(high_low_order):
    print('Trial {}'.format(index+1))

    if rep:
        high_low = "High"
    else:
        high_low = "Low"

    print('Your current task is to count {}'.format(high_low.upper()))
    print("Press Enter when ready")
    input()
    for i in range(5):
        sys.stdout.write('\rThe test starts in {}'.format(5 - i))
        time.sleep(1)
    sys.stdout.write("\r                    \n")

    n_pos = np.random.randint(0.4 * N_SIGNALS, 0.6 * N_SIGNALS)
    order = brains.gen_order(N_SIGNALS, n_pos)
    brains.play(order, INTERVAL, BREAK, S0, S1)

    print("How many {} sounds where there? ".format(high_low.lower()))
    user_count = input()
    if high_low == 'High':
        total = n_pos
    else:
        total = N_SIGNALS - n_pos
    print("Your answer is: {} \n{}\{}\n".format(int(user_count) == total , user_count, total))