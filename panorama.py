import os

import numpy

import scipy.misc
import scipy.signal
import scipy.special

BASE_DIRECTORY = "/Users/bill/workbench/youvisit/__old__/panoramadetect/component/"
CACHE = BASE_DIRECTORY + "cache/"

"""============================================================

discretize(function, size)

Convert a function to an array of values

@param function   = The function to discretize
@param size       = The size of the kernel to outpu

============================================================"""
def discretize(size, function, args=[]):
  kernel    = numpy.empty(size)
  half_size = size / 2

  for i in range(size):
    kernel[i] = function(i - half_size, *args)

  return kernel



"""============================================================

              /       x      \
error(x) = erf| ____________ |
              |           __ |
              \ sigma * -/ 2 /

============================================================"""
def error(x, sigma):
  sigma_times_sqrt_two = sigma * numpy.power(2, 0.5)
  x_over_sigma_times_sqrt_two = x / sigma_times_sqrt_two

  return -scipy.special.erf(x_over_sigma_times_sqrt_two)



"""============================================================

                      1             -1 * (x * mu)^2
gaussian(x) = ________________ * e^      ___________
                        ______           
              sigma * -/2 * pi           2 * sigma^2

============================================================"""
def gaussian(x, mu, sigma, rescale=1):
  sigma_times_sqrt_two_pi = sigma * numpy.power(2 * numpy.pi, 0.5)
  A                       = 1 / sigma_times_sqrt_two_pi

  x_minus_mu_sqrd         = numpy.power(x - mu, 2)
  two_times_sigma_sqrd    = 2 * numpy.power(sigma, 2)
  B                       = -1 * x_minus_mu_sqrd / two_times_sigma_sqrd

  return A * numpy.power(numpy.e, B) / rescale



"""============================================================

               (x - mu)^3
trinomial(x) = __________ + beta

                sigma^2

============================================================"""
def trinomial(x, mu, sigma, beta, high, low):
  x_minus_mu_cubed  = numpy.power(x - mu, 3)
  sigma_sqrd      = numpy.power(sigma, 2)

  return max(min(x_minus_mu_cubed / sigma_sqrd + beta, high), low)



"""============================================================

                           (x - mu)^2
negated binomial(x) = -1 * __________ + beta

                             sigma^2

============================================================"""
def binomial(x, mu, sigma, beta):
  x_minus_mu_sqrd = numpy.power(x - mu, 2)
  sigma_sqrd      = numpy.power(sigma, 2)
  A = x_minus_mu_sqrd / sigma_sqrd

  return -1 * A + beta



"""============================================================

examinePanorama

Determine if a give image is a panorama

@param filename = The location of the panorama

============================================================"""
def examinePanorama(filename):
  name, extension = os.path.splitext(os.path.basename(filename))

  cache = {
    "U": CACHE + name + ".U.npy",
    "R": CACHE + name + ".R.npy",
    "L": CACHE + name + ".L.npy"
  }

  # Load from cache if cached
  if os.path.isfile(cache["U"]) and os.path.isfile(cache["R"]) and os.path.isfile(cache["L"]) and False:
    U = numpy.load(cache["U"])
    R = numpy.load(cache["R"])
    L = numpy.load(cache["L"])

    width = U.shape[0]
    height = R.shape[0]
    aspectRatio = width / height
  else:
    """
    Load image from file as grayscale
    """
    Image  = scipy.misc.imread(filename, True)
    Image  /= 255.0 # compress range from (0, 255) to (0, 1)

    Image  = numpy.reshape(numpy.ravel(Image, order="F"), (Image.shape[1], Image.shape[0])) # reorder so (X, Y) instead of (Y, X)
    # width & height shortcuts
    width  = Image.shape[0]
    height = Image.shape[1]
    aspectRatio = width / height

    """
    Calculate edge diffs
    """
    # Crop edges
    edge = {
      "left":   numpy.ravel(Image[0 : 1, :]),
      "right":  numpy.ravel(Image[width - 1 : width, :]),
      "upper":  numpy.ravel(Image[ :, 0 : 1]),
      "lower":  numpy.ravel(Image[ :, height - 1 : height])
    }

    # Array of median value from upper and lower (for diffing)
    median = {
      "upper": numpy.empty(width, dtype="float32"),
      "lower": numpy.empty(width, dtype="float32")
    }

    median["upper"].fill(numpy.median(edge["upper"]))
    median["lower"].fill(numpy.median(edge["lower"]))

    # Calculate diff
    diff = {
      "delta upper":  numpy.absolute(numpy.subtract(edge["upper"], median["upper"])),
      "left - right": numpy.absolute(numpy.subtract(edge["left"], edge["right"])),
      "delta lower":  numpy.absolute(numpy.subtract(edge["lower"], median["lower"]))
    }

    # Transform edge diffs to reflect "panoramaness"
    U = diff["delta upper"]
    R = diff["left - right"]
    L = diff["delta lower"]

    numpy.save(CACHE + name + ".U", U)
    numpy.save(CACHE + name + ".R", R)
    numpy.save(CACHE + name + ".L", L)

  kernel = discretize(12, trinomial, [1, 5, 10, 1, 0])
  R = scipy.signal.convolve(R, kernel, "same")

  minU = numpy.empty(width,   dtype="float32")
  minR = numpy.empty(height,  dtype="float32")
  minL = numpy.empty(width,   dtype="float32")

  threshold = 0.01

  for i, value in enumerate(U):
    if i == 0 or value < U[i - 1] + threshold and value > U[i - 1] - threshold:
      minU[i] = 0.0
    else:
      minU[i] = 100.0


  for i, value in enumerate(R):
    minR[i] = binomial(value, mu=-0.17, sigma=0.1, beta=6)

  for i, value in enumerate(L):
    if i == 0 or value < L[i - 1] + threshold and value > L[i - 1] - threshold:
      minL[i] = 0.0
    else:
      minL[i] = 100.0

  nR = numpy.sum(minR) / float(height)
  nUL = (numpy.sum(minU) / float(width) + numpy.sum(minL) / float(width)) / 2

  # Transform aspect ratio to reflect "panoramaness"
  mRr = trinomial(aspectRatio, 3.39, 6, 0, 5, 0)
  mULr = gaussian(aspectRatio, 2, 0.01, 2)

  # Calculate "panoramaness"
  pC = mRr + nR
  pS = (mULr - nUL + pC) / 2

  return [pS, pC]




"""============================================================
===============================================================



 CODE BELOW APPLIES TO __main__ ONLY



===============================================================
============================================================"""

def printLoader(cur, tot, msg):
  percent = float(cur) / float(tot)

  stdout.write("\r\t" + `int(percent * 100)` + "%\t")
  full = "processing >> \033[94m" + msg
  stdout.write(full.ljust(50))
  stdout.write("\033[0m")
  stdout.write("\033[43m")
  for pos in range(25):
    if pos < 25 * percent:
      stdout.write(" ")
    else:
      stdout.write("\033[0m")
      stdout.write(" ")
  
  stdout.write("\033[0m")
  stdout.write("<< end")
  stdout.flush()

def main():
  graphs_file = open(OUTPUT, "w")
  i = 0
  sample_number = len(samples)

  for sample in samples:
    P = examinePanorama(SAMPLE + sample["file"])

    graphs_file.write(`i` + " " + `P` + "\n")

    i += 1

    printLoader(i, sample_number, sample["file"])

  stdout.write("\n\n\t~~~ finished! ~~~\n\n")
  graphs_file.close()

def test():
  s, c = examinePanorama(SAMPLE + samples[178]["file"])
  print s
  print c
  """
  file_diff = open(BASE_DIRECTORY + "log/" + `int(time())` + ".txt", "w")
  for j, pixel in enumerate(panorama):
    file_diff.write(`j` + " " + `pixel` + "\n")

  file_diff.close()
  """

if __name__ == "__main__":
  from samples  import samples
  from sys      import stdout
  from time     import time

  SAMPLE = BASE_DIRECTORY + "sample/"
  OUTPUT = BASE_DIRECTORY + "log/" + `int(time())` + ".txt"

  test()
  # main()
