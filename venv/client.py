import brains
import numpy as np
import time
import sys
import os
import errno

# Experiment preparation
# =============CONSTANTS============= #
'''
The Constants for generation of sound signals for experiment
'''
N_SIGNALS = 40
F0 = 310
F1 = 800
F2 = 500
SAMPLE_LEN = .15
INTERVAL = 0.85
N_REPEAT = 30
BREAK = 0

## Defining the sounds
S0 = brains.gen_sound(F0,SAMPLE_LEN)
S1 = brains.gen_sound(F1,SAMPLE_LEN)
S2 = brains.gen_sound(F2,SAMPLE_LEN)

high_low_order = (brains.gen_order(N_REPEAT, N_REPEAT//2))

#SETUP FILES
print("Patient Name:")
patient_name = input()
patient_name = 'output/' + patient_name

valid = False
while not valid:
    try:
        os.mkdir(patient_name)
        valid = True
    except FileExistsError as e:
        if e.errno == errno.EEXIST:
            patient_name += '_n'
        else:
            raise


with open(patient_name + '/config.txt', 'w+') as f:
    f.write("{},{}\n".format('N_SIGNALS', N_SIGNALS))
    f.write("{},{}\n".format('F0', F0))
    f.write("{},{}\n".format('F1', F1))
    f.write("{},{}\n".format('SAMPLE_LEN', SAMPLE_LEN))
    f.write("{},{}\n".format('INTERVAL', INTERVAL))
    f.write("{},{}\n".format('N_REPEAT', N_REPEAT))
with open(patient_name + '/tags.txt', 'w+') as f:
    f.write('')
with open(patient_name + '/experiment_order.txt', 'w+') as f:
    f.write('')
with open(patient_name + '/concentration.txt', 'w+') as f:
    f.write('')

# Running the experiment
for index, rep in enumerate(high_low_order):
    print('Trial {}'.format(index+1))

    if rep:
        high_low = "High"
    else:
        high_low = "Low"

    with open(patient_name + '/experiment_order.txt', 'a') as f:
        f.write(str(int(rep)) + '\n')

    print('Your current task is to count {}'.format(high_low.upper()))
    print("Press Enter when ready")
    input()
    for i in range(5):
        sys.stdout.write('\rThe test starts in {}'.format(5 - i))
        time.sleep(1)
    sys.stdout.write("\r                    \n")

    n_pos = np.random.randint(0.4 * N_SIGNALS//4, 0.6 * N_SIGNALS//4)
    order = brains.gen_order(N_SIGNALS//4, n_pos)

    final_order = np.zeros(N_SIGNALS)
    final_order += 2
    final_order[:N_SIGNALS//4] = order
    brains.shuffle(final_order)

    brains.play(final_order, INTERVAL, BREAK, S0, S1, S2, patient_name)

    print("How many {} sounds where there? ".format(high_low.lower()))
    user_count = input()
    if high_low == 'High':
        total = n_pos
    else:
        total = N_SIGNALS//4 - n_pos
    print("Your answer is: {} \n{}\{}\n".format(int(user_count) == total , user_count, total))
    with open(patient_name + '/concentration.txt', 'a') as f:
        f.write("{},{}\n".format(user_count, total))
