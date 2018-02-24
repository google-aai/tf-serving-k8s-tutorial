import cv2
import numpy as np
import urllib


def resize_and_pad_image(img, output_image_dim):
  """Resize the image to make it IMAGE_DIM x IMAGE_DIM pixels in size.

  If an image is not square, it will pad the top/bottom or left/right
  with black pixels to ensure the image is square.

  Args:
    img: the input 3-color image
    output_image_dim: resized and padded output length (and width)

  Returns:
    resized and padded image
  """

  h, w = img.shape[:2]

  # interpolation method
  if h > output_image_dim or w > output_image_dim:
    # use preferred interpolation method for shrinking image
    interp = cv2.INTER_AREA
  else:
    # use preferred interpolation method for stretching image
    interp = cv2.INTER_CUBIC

  # aspect ratio of image
  aspect = float(w) / h

  # compute scaling and pad sizing
  if aspect > 1:  # Image is "wide". Add black pixels on top and bottom.
    new_w = output_image_dim
    new_h = np.round(new_w / aspect)
    pad_vert = (output_image_dim - new_h) / 2
    pad_top, pad_bot = int(np.floor(pad_vert)), int(np.ceil(pad_vert))
    pad_left, pad_right = 0, 0
  elif aspect < 1:  # Image is "tall". Add black pixels on left and right.
    new_h = output_image_dim
    new_w = np.round(new_h * aspect)
    pad_horz = (output_image_dim - new_w) / 2
    pad_left, pad_right = int(np.floor(pad_horz)), int(np.ceil(pad_horz))
    pad_top, pad_bot = 0, 0
  else:  # square image
    new_h = output_image_dim
    new_w = output_image_dim
    pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

  # scale to IMAGE_DIM x IMAGE_DIM and pad with zeros (black pixels)
  scaled_img = cv2.resize(img, (int(new_w), int(new_h)), interpolation=interp)
  scaled_img = cv2.copyMakeBorder(scaled_img,
                                  pad_top, pad_bot, pad_left, pad_right,
                                  borderType=cv2.BORDER_CONSTANT, value=0)
  return scaled_img


def preprocess_and_encode_images(image_paths, output_image_dim):
  """Read an image, preprocess it, and encode as a jpeg.

  The image can be read from either a local path or url.
  The image must be RGB format.
  Preprocessing involves resizing and padding until the image is exactly
  output_image_dim x output_image_dim in size.
  After preprocessing, the image is encoded as a jpeg string to reduce the
  number of bytes. This jpeg string will be transmitted to the server.

  Args:
    image_paths: list of image paths and/or urls
    output_image_dim: resized and padded output length (and width)

  Returns:
    the same images as a list of jpeg-encoded strings
  """
  jpeg_batch = []

  for image_path in image_paths:
    feature = None
    if 'http' in image_path:
      resp = urllib.urlopen(image_path)
      feature = np.asarray(bytearray(resp.read()), dtype='uint8')
      feature = cv2.imdecode(feature, cv2.IMREAD_COLOR)
    else:
      feature = cv2.imread(image_path)  # Parse the image from your local disk.
    # Resize and pad the image
    feature = resize_and_pad_image(feature, output_image_dim)
    # Append to features_array
    jpeg_image = cv2.imencode('.jpg', feature)[1].tostring()
    jpeg_batch.append(jpeg_image)

  return jpeg_batch