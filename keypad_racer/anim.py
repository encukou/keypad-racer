import time
import functools

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

    def __aiter__(self):
        time_to_wait = self.clock() - self.begin + self.duration
        if time_to_wait > 1:
            return iter([time_to_wait])
        return iter(())

class ConstantValue:
    def __init__(self, end):
        self.end = float(end)

    def __float__(self):
        return self.end

    def __repr__(self):
        return f'<{self.end}>'

    def __aiter__(self):
        return iter(())

def drive(it, dt):
    try:
        time_to_wait = next(it)
    except StopIteration:
        return
    time_to_wait = float(time_to_wait)
    pyglet.clock.schedule_once(functools.partial(drive, it), time_to_wait)

def autoschedule(coro):
    @functools.wraps(coro)
    def func(*args, **kwargs):
        it = coro(*args, **kwargs).__await__()
        drive(it, 0)
    return func

class Wait:
    def __init__(self, time_to_wait):
        self.time_to_wait = time_to_wait

    def __aiter__(self):
        return iter([time_to_wait])

    def __await__(self):
        yield self.time_to_wait
