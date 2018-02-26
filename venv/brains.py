import numpy as np
import time
import sounddevice as sd
import asyncio
from obci.core.messages.types import TagMsg

async def async_play_send(s, ID, send_function):
    '''
    :param s: sound signal
    :param id: id of the trigger
    :param port: the port at which the trigger is sent
    :return: None
    '''
    sd.play(s, 44100)
    t = time.time()
    length = len(s)/44100
    send_function(
                TagMsg(start_timestamp = t, end_timestamp = t + length, name = "sound", channels='-1',
                       desc={'type': "tone{}".format(ID)}))

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

def gen_sound(f, t):
    '''
    :param f: frequency of the generated sound
    :param t: time of the generated sound
    :return: ndarray which represents a sin function in the interval of 0 to t and with the probing frequency of 44100Hz
    '''
    return np.sin(2*np.pi*f*np.arange(0,t,1/44100))

def play(order, interval, break_time, s0, s1, send_function):
    '''
    :param order: order with which the sounds are to be played
    :param interval: the interval between consecutive sounds
    :param s0: the array of the negative sound
    :param s1: the array of the positive sound
    :return:
    '''
    loop = asyncio.get_event_loop()
    for i in order:
        asyncio.sleep(interval)
        if i:
            loop.run_until_complete(async_play_send(s1, 1, send_function))
        else:
            loop.run_until_complete(async_play_send(s0, 0, send_function))
        time.sleep(len(s0)/44100)
    asyncio.sleep(break_time)
    # try:
    #     port.setData(0)
    # except: pass

def shuffle(array):
    '''
    Added to keep the client imports cleaner
    :param array: array to be shuffled
    :return: None
    '''
    np.random.shuffle(array)