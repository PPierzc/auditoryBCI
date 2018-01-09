import numpy as np
import time
import sounddevice as sd
import sys

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

def play(order, interval, s0, s1):
    '''
    :param order: order with which the sounds are to be played
    :param interval: the interval between consecutive sounds
    :param s0: the array of the negative sound
    :param s1: the array of the positive sound
    :return:
    '''
    for i in order:
        time.sleep(interval)
        if i:
            sd.play(s0, 44100)
        else:
            sd.play(s1, 44100)
        time.sleep(len(s0)/44100)
    time.sleep(interval*5)

def shuffle(array):
    '''
    Added to keep the client imports cleaner
    :param array: array to be shuffled
    :return: None
    '''
    np.random.shuffle(array)