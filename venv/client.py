import brains

# Experiment preparation
# =============CONSTANTS============= #
'''
The Constants for generation of sound signals for experiment
'''
N_SIGNALS = 10
N_POSITIVE = 5
F0 = 500
F1 = 310
SAMPLE_LEN = .2
INTERVAL = .5
N_REPEAT = 3

## Defining the sounds
S0 = brains.gen_sound(F0,SAMPLE_LEN)
S1 = brains.gen_sound(F1,SAMPLE_LEN)

## Creating the order array
order = brains.gen_order(N_SIGNALS, N_POSITIVE)

# Running the experiment
for index, rep in enumerate(range(N_REPEAT)):
    print('Trial {}'.format(index+1))
    brains.play(order, INTERVAL, S0, S1)
    brains.shuffle(order)