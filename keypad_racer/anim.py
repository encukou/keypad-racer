import time
import functools
import math

import pyglet

class AnimatedValue:
    def __new__(cls, start, end, duration, *w, **ka):
        if duration <= 0:
            return ConstantValue(end)
        return super().__new__(cls)

    def __init__(self, start, end, duration, easing=lambda x:x):
        self.start = start
        self.end = float(end)
        self.clock = clock = time.monotonic
        self.begin = clock()
        self.duration = duration
        self.easing = easing

    def __float__(self):
        t = (self.clock() - self.begin) / self.duration
        if t > 1:
            # Evil metamorphosis
            self.val = self.end
            self.__class__ = ConstantValue
            del self.start
            return self.end
        start = float(self.start)
        t = self.easing(t)
        return (1-t) * start + t * self.end

    def __repr__(self):
        return f'<{self.start}→{self.end}:{float(self)}>'

    def __await__(self):
        time_to_wait = self.clock() - self.begin + self.duration
        if time_to_wait > 1:
            yield time_to_wait
        return self

class ConstantValue:
    def __init__(self, end):
        self.end = float(end)

    def __float__(self):
        return self.end

    def __repr__(self):
        return f'<{self.end}>'

    def __await__(self):
        return self
        yield

def drive(it, dt=0):
    go = functools.partial(drive, it)
    try:
        time_or_blocker = next(it)
    except StopIteration:
        return
    if isinstance(time_or_blocker, Blocker):
        time_or_blocker.waiters.append(go)
    else:
        time_to_wait = float(time_or_blocker)
        pyglet.clock.schedule_once(go, time_to_wait)

def autoschedule(coro):
    @functools.wraps(coro)
    def func(*args, **kwargs):
        blocker = Blocker()
        async def wrap():
            await coro(*args, **kwargs)
            blocker.unblock()
        it = wrap().__await__()
        drive(it, 0)
        return blocker
    return func

def fork(coro):
    it = coro().__await__()
    drive(it, 0)

class Wait:
    def __init__(self, time_to_wait):
        self.time_to_wait = time_to_wait

    def __await__(self):
        yield self.time_to_wait

class Blocker:
    def __init__(self):
        self.done = False
        self.waiters = []

    def unblock(self):
        self.done = True
        for waiter in self.waiters:
            waiter()
        self.waiters.clear()

    def __await__(self):
        if not self.done:
            yield self

def cubic_inout(t):
    if t < 0.5:
        return 4 * t ** 3
    p = 2 * t - 2
    return 0.5 * p ** 3 + 1

def sine_inout(t):
    return 0.5 * (1 - math.cos(t * math.pi))


def sine_in(t):
    return math.sin((t - 1) * math.pi / 2) + 1


def sine_out(t):
    return math.sin(t * math.pi / 2)
