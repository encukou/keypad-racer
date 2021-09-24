import time

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
        print(t, self.easing)
        print(self.easing(t))
        t = self.easing(t)
        return (1-t) * start + t * self.end

    def __repr__(self):
        return f'<{self.start}→{self.end}:{float(self)}>'

class ConstantValue:
    def __init__(self, end):
        self.end = float(end)

    def __float__(self):
        return self.end

    def __repr__(self):
        return f'<{self.end}>'
