from panorama import Panorama
from sys import stdout

#"""

files = {
  "yes": {
    "sphere": {
      "1.jpg",
      "2.jpg",
      "3.jpg",
      "4.jpg",
      "5.jpg",
      "6.jpg",
      "7.jpg",
      "8.jpg",
      "9.jpg"
    },
    "cylinder": {
      "1.jpg",
      "2.jpg",
      "3.jpg",
      "4.jpg",
      "5.jpg"
    },
  },
  "no": {
    "1.jpg",
    "2.jpg",
    "3.jpg",
    "4.jpg",
    "5.jpg",
    "6.jpg",
    "7.jpg",
    "8.jpg",
    "9.jpg",
    "10.jpg",
    "11.jpg",
    "12.jpg",
    "13.jpg",
    "14.jpg",
    "15.jpg",
    "16.jpg",
    "17.jpg",
    "18.jpg",
    "19.jpg",
    "20.jpg",
    "21.jpg",
    "22.jpg",
    "23.jpg",
    "24.jpg",
    "25.jpg",
    "26.jpg",
  }
}

"""

files = {
  "yes": {
    "sphere": {
      "1.jpg"
    },
    "cylinder": {
      "1.jpg"
    }
  },
  "no": {
    "17.jpg"
  }
}

"""

lists = [
  {
    "names": files["yes"]["sphere"],
    "from": "components/data/yes/sphere/",
    "as": "components/graphs/spheres.txt",
    "call": "Sphere"
  },
  {
    "names": files["yes"]["cylinder"],
    "from": "components/data/yes/cylinder/",
    "as": "components/graphs/cylinders.txt",
    "call": "Cylinder"
  },
  {
    "names": files["no"],
    "from": "components/data/no/",
    "as": "components/graphs/none.txt",
    "call": "None"
  },
]

total = 39.0
ii = 0.0

for list in lists:
  i = 0
  f = open(list["as"], "w")

  for name in list["names"]:
    P = Panorama(list["from"] + name)
    f.write(`i` + " " + `P.isSphere` + "\n")
    i += 1

    dd = ii / total
    stdout.write("\r" + `int(dd * 100)` + "%\t|")
    for jj in range(25):
      if jj < 25 * dd:
        stdout.write("=")
      else:
        stdout.write(".")
    stdout.write("|")
    stdout.flush()
    ii += 1

  f.close()

stdout.write("\ndone!")
