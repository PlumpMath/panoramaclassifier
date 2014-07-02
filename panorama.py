import numpy            as np

from scipy.misc         import imread
from scipy.special      import erf
from scipy              import signal

class Panorama:
  def __init__(self, file):
    self.load(file)

    self.threshold = {
      "cylinder": 150,
      "sphere": 150
    }

    t, lr, b = self.delta()
    self.isCylinder, self.isSphere = self.computeFromDeltas(t, lr, b)

  def load(self, file):
    self.data             = imread(file, True)

    self.h, self.w        = self.data.shape
    self.wh               = float(self.w) / float(self.h) or 1
    self.halfw            = int(np.ceil(self.w / 2))

    return self.data

  def delta(self):
    ww  = self.halfw if self.halfw == self.w - self.halfw else self.halfw + 1

    t   = np.absolute(np.subtract(self.data[0 : 1, 0 : ww], np.fliplr(self.data[0 : 1, self.halfw : self.w])))
    _lr = np.absolute(np.subtract(self.data[0 : self.h, 0 : 1], self.data[0 : self.h, self.w - 1 : self.w]))
    lr  = np.empty(len(_lr))
    b   = np.absolute(np.subtract(self.data[self.h - 1: self.h, 0 : ww], np.fliplr(self.data[self.h - 1: self.h, self.halfw : self.w])))

    for index, item in enumerate(_lr):
      lr[index] = item.flatten()

    t = t[0]
    b = b[0]
    
    return t, lr, b

  def mutateRatioSphere(self, x):
    sigma = 0.1
    return (1 / (sigma * np.power(2 * np.pi, 0.5))) * np.power(np.e, -1 * (np.power(x - 2, 2) / (2 * np.power(sigma, 2)))) / 2

  def mutateRatioCylinder(self, x):
    return max(np.power(x, 3) / 100, 1)

  def erfKernel(self, size):
    kernel = np.empty((size))

    for index in range(size):
      kernel[index] = erf(index)

    return kernel

  def computeFromDeltas(self, t, lr, b):

    a = signal.convolve(t, self.erfKernel(6), "same")
    b = signal.convolve(lr, self.erfKernel(6), "same")
    c = signal.convolve(b, self.erfKernel(6), "same")

    s = np.power(float(len(b[b>self.threshold["cylinder"]])) / (self.w * self.h) * 10000, 1.8)
    ss = float(len(a[a>self.threshold["sphere"]]) + len(c[c>self.threshold["sphere"]])) / (self.w * self.h) * 1000 + s

    sm = self.mutateRatioCylinder(self.wh)
    ssm = self.mutateRatioSphere(self.wh)

    return sm - s >= 0.9999, ssm - ss >= 1
