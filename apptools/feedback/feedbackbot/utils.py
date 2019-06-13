""" 
This module provides some helper functions for the feedback plugin. These
functions are designed to be used by the user-developer so that the feedback
plugin can be used in their application. 
"""

from PyQt4.QtGui import QPixmap
import numpy as np

def take_screenshot_qimg(info):
    """ Take screenshot of an active GUI widget. 

     Parameters
     ----------
     info: traitsui.UIInfo
         The UIInfo instance which contains the active widget.
     
     Returns:
     --------
     qimg: PyQt4.QtGui.QImage
        Screenshot image as PyQt4.QtGui.QImage instance. 

     """

    pixmap = QPixmap.grabWidget(info.ui.control)

    qimg = pixmap.toImage()

    return qimg

def get_raw_qimg_data(qimg):
    """ Get raw image data (BGR[A] values, and size in pixels).

    Parameters:
    qimg: PyQt4.QtGui.Qimage instance

    Returns:
    --------
    bytes 
        Raw bytes ordered as BGR[A]. Alpha channel is included if available.
    int 
        Image height in pixels.
    int 
        Image width in pixels.

    """

    qbits = qimg.bits()

    num_channels = qimg.depth() // 8
    
    qbits.setsize(qimg.width() * qimg.height() * num_channels)

    return [qbits.asstring(), qimg.height(), qimg.width()]

def bgr_bytes_to_rgb_bytes(bgr_bytes, height, width):
    """ Convert BGR[A] bytestring to RGB[A] bytestring.

    Note
    ----
    This function is designed to convert the BGR[A]-ordered
    bytestring of a PyQt4.QtGui.QImage into RGB[A] ordering.
    An alpha-channel is not necessary, but will be handled if provided.

    Parameters
    ----------
    bgr_bytes: bytes
        BGR[A]-ordered bytestring.

    height: int
        Height of image in pixels.

    width: int
        Height of image in pixels.

    Returns
    -------
    bytes
        RGB[A]-ordered bytes

    """

    bgr_mat = bytes_to_matrix(bgr_bytes, height, width)

    num_channels = bgr_mat.shape[2]

    if num_channels == 3:

        new_channel_idx = [2, 1, 0]

    elif num_channels == 4:

        new_channel_idx = [2, 1, 0, 3]

    else: 

        raise ValueError(
            "Image has {} channels. Expected 3 or 4.".format(num_channels))

    return bgr_mat[..., new_channel_idx].tobytes()

def bytes_to_matrix(bytes_str, height, width):

    return np.ascontiguousarray(np.frombuffer(
        bytes_str, dtype=np.uint8).reshape(height, width, -1))

def bytes_to_buffer(bytes_str, height, width, fmt):

    img = Image.frombytes('RGBA', (width, height), bytes_str)

    buf = io.BytesIO()

    img.save(buf, fmt)
    buf.seek(0)

    return buf

