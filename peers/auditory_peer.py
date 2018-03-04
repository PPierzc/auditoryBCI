import asyncio
import time
import numpy as np
import pyaudio
import wave
import sys
from scipy.io.wavfile import write

import pygame

from obci.core.configured_peer import ConfiguredPeer
from obci.utils.message_helpers import send_tag
from obci.core.messages.types import SignalMessage
from obci.core.message_handler_mixin import subscribe_message_handler
from obci.interfaces.bci.p300.sounds import Sound

__all__ = ('AutoTagGenerator',)


N_SIGNALS = 40
F0 = 310
F1 = 500
SAMPLE_LEN = .3
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
    scaled = np.int16(data/np.max(np.abs(data)) * 32768)
    write(file_name, 44100, scaled)
    return file_name

def run_sound(file_path):
    CHUNK = 32768

    wf = wave.open(file_path, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data. pyaudio.paContinue)
    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=44100,
                    output=True,
                    frames_per_buffer=CHUNK,
                    stream_callback = callback,
                    output_device_index = 0)

    # # read data
    # data = wf.readframes(CHUNK)

    # # play stream (3)
    # while len(data) > 0:
    #     stream.write(data)
    #     data = wf.readframes(CHUNK)
    stream.start_stream()
    while stream.is_active():
        asyncio.sleep(0.1)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    wf.close()

    # close PyAudio (5)
    p.terminate()

S0 = gen_sound(F0,SAMPLE_LEN)
S1 = gen_sound(F1,SAMPLE_LEN)

S0_path = save_array_to_file('/home/pawel/s0.wav', S0)
S1_path = save_array_to_file('/home/pawel/s1.wav', S1)

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
S_0 = pygame.mixer.Sound(S0_path)
S_1 = pygame.mixer.Sound(S1_path)

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

                        S_1.play()
                    else: 
                        await send_tag(self, t, t + SAMPLE_LEN, 'LOW',
                               {
                                "FREQ": "LOW"
                                }
                               )
                        S_0.play()
                    await asyncio.sleep(INTERVAL + SAMPLE_LEN)
                await asyncio.sleep(BREAK)

    @subscribe_message_handler(SignalMessage)
    async def handle_sig(self, msg):
        print(msg)
        print(msg.data.samples)
