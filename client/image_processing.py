from PIL import Image
import cv2
import StringIO
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

  old_size = img.size  # old_size[0] is in (width, height) format

  ratio = float(output_image_dim) / max(old_size)
  new_size = tuple([int(x * ratio) for x in old_size])
  # use thumbnail() or resize() method to resize the input image

  # thumbnail is a in-place operation

  # im.thumbnail(new_size, Image.ANTIALIAS)

  scaled_img = img.resize(new_size, Image.ANTIALIAS)
  # create a new image and paste the resized on it

  padded_img = Image.new("RGB", (output_image_dim, output_image_dim))
  padded_img.paste(scaled_img, ((output_image_dim - new_size[0]) // 2,
                    (output_image_dim - new_size[1]) // 2))

  return padded_img


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
    image = None
    if 'http' in image_path:
      image = Image.open(urllib.urlopen(image_path))
    else:
      image = Image.open(image_path)  # Parse the image from your local disk.
    # Resize and pad the image
    image = resize_and_pad_image(image, output_image_dim)
    jpeg_image = StringIO.StringIO()
    image.save(jpeg_image, format='JPEG')
    # Append to features_array
    jpeg_batch.append(jpeg_image.getvalue())

  return jpeg_batch