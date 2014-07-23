(function ()
{
  function discretize(size, closure, args)
  {
    var size = size|0;
    var args = args || null;

    var kernel = zeroes(size);
    var half_size = (size / 2)|0;

    for (var i = size; i -= 1;) {
      var x = (i - half_size)|0;
      kernel[i] = +closure.apply(null, [x].concat(args));
    }

    return kernel;
  }

  function erf(x)
  {
    var a1 =  0.254829592;
    var a2 = -0.284496736;
    var a3 =  1.421413741;
    var a4 = -1.453152027;
    var a5 =  1.061405429;
    var p  =  0.3275911;

    var sign = 1;
    if (x < 0) {
        sign = -1;
    }
    x = Math.abs(x);

    var t = 1.0 / (1.0 + p * x);
    var y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return sign * y;
  }

  function error(x, sigma)
  {
    var sqrttwo = 1.414213562;

    return erf(x / (sigma * sqrttwo));
  }

  function gaussian(x, mu, sigma, rescale)
  {
    var rescale = (rescale || 1);

    var a = 2.506628274;

    return (1 / (sigma * a)) * Math.exp(Math.E, -1 * Math.exp(x - mu, 2) / 2 * Math.exp(sigma, 2)) / rescale;
  }

  function trinomial(x, mu, sigma, beta, upper, lower)
  {
    var y = Math.exp(x - mu, 3) / Math.exp(sigma, 2) + beta;

    return Math.max(Math.min(y, upper), lower);
  }

  function binomial(x, mu, sigma, beta)
  {
    return -1 * Math.exp(x - mu, 2) / Math.exp(sigma, 2) + beta;
  }

  function crop(grid, x, y, w, h)
  {
    var crop = [];

    var yy = y + h;
    var xx = x + w;

    for (var i = x, j = 0; i < xx; i += 1, j += 1) {
      crop[j] = grid[i].slice(y, yy);
    }

    return grid;
  }

  function diff(a, b)
  {
    if (Object.prototype.toString.call(b) === '[object Array]')
      return a.map(function (x, i)
      {
        return -b[i] + x;
      });
    else
      return a.map(function (x, i)
      {
        return -b + x;
      });
  }

  function median(a)
  {
    return a.reduce(function (a, b)
    {
      return a + b;
    }) / a.length;
  }

  function zeroes(l)
  {
    return Array.apply(null, new Array(l)).map(Number.prototype.valueOf, 0);
  }

  function expand(a)
  {
    return [0].concat(a, [0]);
  }

  function pad(a, l)
  {
    if (l > 0) return pad(expand(a), l - 1);
    else return a;
  }

  function convolve_iter(a, k, o)
  {
    return o.map(function (x, i)
    {
      return k.reduce(function (y, z, j)
      {
        return y + a[i + j]*z;
      }, 0) || x;
    });
  }

  function convolve(a, k, full)
  {
    var output = convolve_iter(pad(a, -1 + k.length), k.reverse(), zeroes(-1 + a.length + k.length));

    if (full) return output;
    else return output.slice(0, a.length);
  }

  function RGBtoY(rgb)
  {
    var gamma = 2.2;
    var rgb = rgb.map(function (x)
    {
      return Math.pow(x/255.0, gamma);
    });

    return 0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2];
  }

  function imload(src, callback)
  {
    var img = new Image;
    img.src = src;
    img.onload = callback;
  }

  function imread(img)
  {
    var width = img.width;
    var height = img.height;

    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;

    var context = canvas.getContext('2d');
    context.drawImage(img, 0, 0);

    var data = context.getImageData(0, 0, width, height).data;

    return zeroes(width).map(function (w, x)
    {
      return zeroes(height).map(function (z, y)
      {
        return RGBtoY([
          data[(y*width + x)*4 + 0],
          data[(y*width + x)*4 + 1],
          data[(y*width + x)*4 + 2]
        ])*255;
      });
    });
  }

  var t = 0.01;

  function threshold(total, x, i, array)
  {
    if (i == 0 || x < array[i - 1] + t && x > array[i - 1] - t)
      return total;
    else
      return total + 100.0;
  }

  function examine(img, width, height)
  {
    var aspectRatio = +(width / height);

    var left_edge   = crop(img, 0, 0, 1, height);
    var right_edge  = crop(img, width - 1, 0, 1, height);
    var upper_edge  = crop(img, 0, 0, width, 1);
    var lower_edge  = crop(img, 0, height - 1, width, 1);

    var upper_median = median(upper_edge);
    var lower_median = median(lower_edge);

    var delta_upper = diff(upper_edge, upper_median);
    var delta_lr    = diff(left_edge, right_edge);
    var delta_lower = diff(lower_edge, lower_median);

    var kernel = discretize(12, trinomial, [1, 5, 10, 1, 0]);
    var convolved_lr = convolve(delta_lr, kernel);

    var rU = delta_upper.reduce(threshold, 0);
    var rR = convolved_lr.reduce(function (total, x)
    {
      return total + binomial(x, -0.17, 0.1, 6);
    });
    var rL = delta_lower.reduce(threshold, 0);

    var nR  = rR / height;
    var nUL = (rU + rL)/(width*2);

    var mRr = trinomial(aspectRatio, 3.39, 6, 0, 5, 0);
    var mULr = gaussian(aspectRatio, 2, 0.01, 2);

    pC = mRr + nR;
    pS = (mULr - nUL + pC) / 2;

    return [pC, pS];
  }

  var src = '//localhost:8000/component/lenna.jpg';

  imload(src, function (e) {
    console.log(examine(imread(this), this.width, this.height));
  });

})();
