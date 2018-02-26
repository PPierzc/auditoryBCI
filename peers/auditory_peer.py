# import asyncio
# from obci.core.configured_peer import ConfiguredPeer
# from obci.core.messages.types import TagMsg, SignalMessage
# import time
# from obci.core.message_handler_mixin import subscribe_message_handler

# __all__ = ('InterfacePeer',)

# class InterfacePeer(ConfiguredPeer):

#     async def _connections_established(self):
#         await super()._connections_established()
#         self.create_task(self.random_tags())
#         await self.ready()

#     async def _start(self):
#         await super()._start()
#         self.create_task(self._run())

#     async def _run(self):
#         while True:
#             await asyncio.sleep(5)
#             self.send_message(TagMsg(start_timestamp=time.time(), end_timestamp=time.time(), name='dzwiek', channels='-1', desc={'type':'ton1'}))

#     @subscribe_message_handler(SignalMessage)
#     async def handle_sig(self, msg):
#         print(msg)
#         print(msg.data.samples)

        
# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module providing dummy tag sender peer.

Author:
     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import asyncio
import random
import time
import numpy as np

from obci.core.configured_peer import ConfiguredPeer
from obci.utils.message_helpers import send_tag
from obci.core.messages.types import SignalMessage
from obci.core.message_handler_mixin import subscribe_message_handler


COLORS = ['czerwony', 'zielony', 'niebieski', 'bialy']
NAMES = ['pozytywny', 'negatywny', 'neutralny']
__all__ = ('AutoTagGenerator',)


N_SIGNALS = 40
F0 = 310
F1 = 500
SAMPLE_LEN = .15
INTERVAL = 0.85
N_REPEAT = 30
BREAK = 5

def gen_sound(f, t):
    '''
    :param f: frequency of the generated sound
    :param t: time of the generated sound
    :return: ndarray which represents a sin function in the interval of 0 to t and with the probing frequency of 44100Hz
    '''
    return np.sin(2*np.pi*f*np.arange(0,t,1/44100))

def gen_order(n_signals, n_positive): # Binomial Case
    '''
    :param n_signals: Number of sound signals
    :param n_positive: Number of positive signals
    :return: ndarray with a random order containing 0s and 1s, where 1s represent the positive signals
    '''
    order = np.zeros(n_signals)
    order[:n_positive] = 1
    np.random.shuffle(order)
    return order


S0 = gen_sound(F0,SAMPLE_LEN)
S1 = gen_sound(F1,SAMPLE_LEN)

high_low_order = gen_order(N_REPEAT, N_REPEAT//2)

class AutoTagGenerator(ConfiguredPeer):
    """Peer which randomly sends meaningless tags."""

    async def _connections_established(self):
        await super()._connections_established()
        await self.ready()

    async def _start(self):
        await super()._start()
        self.create_task(self._run())

    async def _run(self):
        while True:

            for index, rep in enumerate(high_low_order):
                n_pos = np.random.randint(0.4 * N_SIGNALS, 0.6 * N_SIGNALS) # Generate a random number of positive signals
                order = gen_order(N_SIGNALS, n_pos) # Create the order with given positive signals
                for i in order:
                    t = time.time()
                    if i:
                        await send_tag(self, t, t + SAMPLE_LEN, 'HIGH',
                               {
                                "FREQ": "HIGH"
                                }
                               )
                    else: 
                        await send_tag(self, t, t + SAMPLE_LEN, 'LOW',
                               {
                                "FREQ": "LOW"
                                }
                               )
                    await asyncio.sleep(INTERVAL + SAMPLE_LEN)
                await asyncio.sleep(BREAK)

    @subscribe_message_handler(SignalMessage)
    async def handle_sig(self, msg):
        print(msg)
        print(msg.data.samples)
