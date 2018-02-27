import asyncio
import time
import numpy as np
import pyaudio
import wave
import sys
from scipy.io.wavfile import write

from obci.core.configured_peer import ConfiguredPeer
from obci.utils.message_helpers import send_tag
from obci.core.messages.types import SignalMessage
from obci.core.message_handler_mixin import subscribe_message_handler

__all__ = ('AutoTagGenerator',)


N_SIGNALS = 40
F0 = 310
F1 = 500
SAMPLE_LEN = .5
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

def save_array_to_file(file_name, data):
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    write(file_name, 44100, scaled)
    return file_name

def run_sound(file_path):
    CHUNK = 128

    wf = wave.open(file_path, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()

S0 = gen_sound(F0,SAMPLE_LEN)
S1 = gen_sound(F1,SAMPLE_LEN)

S0_path = save_array_to_file('/home/pawel/s0.wav', S0)
S1_path = save_array_to_file('/home/pawel/s1.wav', S1)


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
        global S1_path
        global S0_path
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

                        run_sound(S1_path)
                    else: 
                        await send_tag(self, t, t + SAMPLE_LEN, 'LOW',
                               {
                                "FREQ": "LOW"
                                }
                               )
                        run_sound(S0_path)
                    await asyncio.sleep(INTERVAL + SAMPLE_LEN)
                await asyncio.sleep(BREAK)

    @subscribe_message_handler(SignalMessage)
    async def handle_sig(self, msg):
        print(msg)
        print(msg.data.samples)
