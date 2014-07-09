import os

import numpy

import scipy.misc
import scipy.signal
import scipy.special

BASE_DIRECTORY = "/Users/bill/Projects/youvisit/panoramadetect/component/"
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
def highpass(x, mu, sigma, beta):
  x_minus_mu_cubed  = numpy.power(x - mu, 3)
  sigma_sqrd      = numpy.power(sigma, 2)

  return max(min(x_minus_mu_cubed / sigma_sqrd + beta, 1), 0)



"""============================================================

                           (x - mu)^2
negated binomial(x) = -1 * __________ + beta

                             sigma^2

============================================================"""
def lowpass(x, mu, sigma, beta):
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
  name, extension = os.path.splitext(filename)

  cache = {
    "U": CACHE + name + ".U",
    "R": CACHE + name + ".R",
    "L": CACHE + name + ".L"
  }

  # Load from cache if cached
  if os.path.isfile(cache["U"]) and os.path.isfile(cache["R"]) and os.path.isfile(cache["L"]):
    U = numpy.load(cache["U"])
    R = numpy.load(cache["R"])
    L = numpy.load(cache["L"])
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

  kernel = discretize(12, highpass, [0.1, 0.1, 0])
  R = scipy.signal.convolve(R, kernel, "same")

  minR = numpy.empty(height, dtype="float32")
  maxR = numpy.empty(height, dtype="float32")

  for i, value in enumerate(R):
    minR[i] = lowpass(value, mu=-0.17, sigma=0.1, beta=6)
    maxR[i] = highpass(value, mu=0.05, sigma=0.05, beta=0.1)

  nR = (numpy.sum(minR) / float(height)) / numpy.power(10, 1)

  # Transform aspect ratio to reflect "panoramaness"
  # Calculate "panoramaness"

  return nR




"""============================================================
===============================================================



 CODE BELOW APPLIES TO __main__ ONLY



===============================================================
============================================================"""

def printLoader(cur, tot):
  percent = float(cur) / float(tot)

  stdout.write("\r" + `int(percent * 100)` + "%\t[[")

  for pos in range(25):
    if pos < 25 * percent:
      stdout.write("*")
    else:
      stdout.write(" ")

  stdout.write("]]")
  stdout.flush()

def main():
  f_s = open("sphere.txt", "w")
  f_c = open("cylind.txt", "w")
  i = 0
  sample_number = len(samples)

  for sample in samples:
    P = examinePanorama(SAMPLE + sample["file"])

    f_s.write(`i` + " " + `P` + "\n")

    i += 1

    printLoader(i, sample_number)

  print "\n"
  f_s.close()
  f_c.close()

def test():
  diff = [None, None, None]

  diff[0] = examinePanorama(SAMPLE + samples[0]["file"])
  diff[1] = examinePanorama(SAMPLE + samples[1]["file"])

  i = 2

  while samples[i]["type"] != "none":
    i += 1

  diff[2] = examinePanorama(SAMPLE + samples[i]["file"])

  for i in range(3):
    file_diff = open("diff_" + `i` + ".txt", "w")
    for j in range(len(diff[i])):
      file_diff.write(`j` + " " + `diff[i][j] * 10000` + "\n")

    file_diff.close()

if __name__ == "__main__":
  from samples  import samples
  from sys      import stdout

  SAMPLE = BASE_DIRECTORY + "sample/"

  # test()
  main()
