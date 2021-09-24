import time

class AnimatedValue:
    def __init__(self, start, end, duration):
        self.start = start
        self.end = float(end)
        self.clock = clock = time.monotonic
        self.begin = clock()
        self.duration = duration

    def __float__(self):
        t = (self.clock() - self.begin) / self.duration
        if t > 1:
            # Evil metamorphosis
            self.val = self.end
            self.__class__ = ConstantValue
            del self.start
            return self.end
        start = float(self.start)
        return (1-t) * start + t * self.end

    def __repr__(self):
        return f'<{self.start}→{self.end}:{float(self)}>'

class ConstantValue:
    def __init__(self, val):
        self.val = float(val)

    def __float__(self):
        return self.val

    def __repr__(self):
        return f'<{self.val}>'
