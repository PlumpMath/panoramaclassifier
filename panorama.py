import numpy            as np

from scipy.misc         import imread
from scipy.special      import erf
from scipy              import signal

from matplotlib import pyplot as plt

"""============================================================

discretize(function, size)

Convert a function to an array of values

@param function   = The function to discretize
@param size       = The size of the kernel to outpu

============================================================"""
def discretize(function, size):
  kernel    = np.empty(size)
  half_size = size / 2

  for i in range(size):
    kernel[i] = function(i - half_size)

  return kernel



"""============================================================

              /       x      \
error(x) = erf| ____________ |
              |           __ |
              \ sigma * -/ 2 /

============================================================"""
def error(x, sigma):
  sigma_times_sqrt_two = sigma * np.power(2, 0.5)
  x_over_sigma_times_sqrt_two = x / sigma_times_sqrt_two

  return np.erf(x_over_sigma_times_sqrt_two)



"""============================================================

                      1             -1 * (x * mu)^2
gaussian(x) = ________________ * e^      ___________
                        ______           
              sigma * -/2 * pi           2 * sigma^2

============================================================"""
def gaussian(x, mu, sigma, rescale=1):
  sigma_times_sqrt_two_pi = sigma * np.power(2 * np.pi, 0.5)
  A                       = 1 / sigma_times_sqrt_two_pi

  x_minus_mu_sqrd         = np.power(x - mu, 2)
  two_times_sigma_sqrd    = 2 * np.power(sigma, 2)
  B                       = -1 * x_minus_mu_sqrd / two_times_sigma_sqrd

  return A * np.power(np.e, B) / rescale



"""============================================================

                                    1
stepped inverted trinomial(x) = __________ * sigma^2

                                (x - mu)^3

============================================================"""
def sit(x, mu, sigma, cutoff):
  if x > mu:
    x_minus_mu_cubed = np.power(x - mu, 3)
    one_over_x_minus_mu_cubed = 1 / x_minus_mu_cubed

    return min(one_over_x_minus_mu_cubed * np.power(sigma, 2), cutoff)
  else:
    return cutoff



"""============================================================

examinePanorama

Determine if a give image is a panorama

@param filename = The location of the panorama

============================================================"""
def examinePanorama(filename):
  """
  Load image from file as grayscale
  """
  Image  = imread(filename, True)
  Image  /= 255.0 # compress range from (0, 255) to (0, 1)

  Image  = np.reshape(np.ravel(Image, order="F"), (Image.shape[1], Image.shape[0])) # reorder so (X, Y) instead of (Y, X)
  # width & height shortcuts
  width  = Image.shape[0]
  height = Image.shape[1]

  """
  Define necessary parameters
  """
  threshold = 0.008

  """
  Calculate edge diffs
  """
  # Crop edges
  edge = {
    "left":   np.ravel(Image[0 : 1, :]),
    "right":  np.ravel(Image[width - 1 : width, :]),
    "upper":  np.ravel(Image[ :, 0 : 1]),
    "lower":  np.ravel(Image[ :, height - 1 : height])
  }

  # Array of median value from upper and lower (for diffing)
  median = {
    "upper": np.empty(width, dtype="float32"),
    "lower": np.empty(width, dtype="float32")
  }

  median["upper"].fill(np.median(edge["upper"]))
  median["lower"].fill(np.median(edge["lower"]))

  # Calculate diff
  diff = {
    "delta upper":  np.absolute(np.subtract(edge["upper"], median["upper"])),
    "left - right": np.absolute(np.subtract(edge["left"], edge["right"])),
    "delta lower":  np.absolute(np.subtract(edge["lower"], median["lower"]))
  }

  # Transform edge diffs to reflect "panoramaness"
  U = diff["delta upper"]
  R = diff["left - right"]
  L = diff["delta lower"]

  tR = np.empty(height, dtype="float32")

  for i, value in enumerate(R):
    tR[i] = sit(value, 0, 0.0001, 2)

  nR = (np.sum(tR) / float(height)) / 1000

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
    P = examinePanorama(BASE_DIRECTORY + sample["file"])

    f_s.write(`i` + " " + `P` + "\n")

    i += 1

    printLoader(i, sample_number)

  print "\n"
  f_s.close()
  f_c.close()

def test():
  diff = [None, None, None]

  diff[0] = examinePanorama(BASE_DIRECTORY + samples[0]["file"])
  diff[1] = examinePanorama(BASE_DIRECTORY + samples[1]["file"])

  i = 2

  while samples[i]["type"] != "none":
    i += 1

  diff[2] = examinePanorama(BASE_DIRECTORY + samples[i]["file"])

  for i in range(3):
    file_diff = open("diff_" + `i` + ".txt", "w")
    for j in range(len(diff[i])):
      file_diff.write(`j` + " " + `diff[i][j] * 10000` + "\n")

    file_diff.close()

if __name__ == "__main__":
  from samples  import samples
  from sys      import stdout

  BASE_DIRECTORY = "/Users/bill/Projects/youvisit/panoramadetect/v2/component/sample/"

  # test()
  main()
