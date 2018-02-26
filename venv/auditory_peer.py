import brains
import numpy as np
import asyncio
from obci.core.configured_peer import ConfiguredPeer
from obci.core.messages.types import TagMsg, SignalMessage
import time
from obci.core.message_handler_mixin import subscribe_message_handler
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

__all__ = ('InterfacePeer',)


class InterfacePeer(ConfiguredPeer):

    async def _connections_established(self):
        await super()._connections_established()
        self.create_task(self.random_tags())
        await self.ready()

    async def run_experiment(self):
        while True:
            # Running the experiment
            for index, rep in enumerate(high_low_order):
                n_pos = np.random.randint(0.4 * N_SIGNALS, 0.6 * N_SIGNALS) # Generate a random number of positive signals
                order = brains.gen_order(N_SIGNALS, n_pos) # Create the order with given positive signals
                brains.play(order, INTERVAL, BREAK, S0, S1, self.send_message)

    @subscribe_message_handler(SignalMessage)
    async def handle_sig(self, msg):
        print(msg)
        print(msg.data.samples)


