from samples import samples
from PIL import Image

from os.path import splitext

BASE_DIRECTORY = "/Users/bill/Projects/youvisit/panoramadetect/component/sample/"

def buildCylindricalSamples(filename, ratios):
  print "processing " + filename

  name, ext = splitext(filename)

  im    = [None, None]
  im[0] = Image.open(BASE_DIRECTORY + filename)

  w     = im[0].size[0]
  h     = [0, 0]
  h[0]  = im[0].size[1]

  ratio     = w / h[0]

  for r in ratios:
    if ratio < r:
      print "at ratio " + `r`

      h[1] = w / r

      diff = (h[0] - h[1]) / 2

      left = 0
      right = w
      upper = 0 + diff
      lower = h[0] - diff

      samples.append({
        "file": name + "." + `r` + ext,
        "type": "none-cylindrical"
      })

      im[1] = im[0].crop((left, upper, right, lower))
      im[1].save(BASE_DIRECTORY + name + "." + `r` + ext)

for sample in samples:
  if sample["type"] == "none":
    buildCylindricalSamples(sample["file"], range(3, 9))

print samples
