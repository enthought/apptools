""" 
This module provides some helper functions for the feedback plugin. These
functions are designed to be used by the user-developer so that the feedback
plugin can be used in their application. 
"""

import io

from pyface.qt.QtGui import QPixmap
from pyface.qt.QtCore import QBuffer
from PIL import Image
import numpy as np

from .model import FeedbackMessage
from .view import FeedbackController

def take_screenshot_qimage(control):
    """ Take screenshot of an active GUI widget. 

     Parameters
     ----------
     control : `QtGui.QWidget`
        GUI widget that will be grabbed.

     Returns:
     --------
     qimg : `QtGui.QImage`
        The screenshot image.

     """

    return QPixmap.grabWidget(control).toImage()

def qimage_to_rgb_array(qimg):
    """ Converts a `QImage` instance to a numeric RGB array containing pixel data.

    Parameters
    ----------
    qimg : `QtGui.QImage` 
        Image to convert to array.

    Returns
    -------
    img_array : `numpy.ndarray`
        A 3D array containing pixel data in RGB format.

    Note
    ----
    If an Alpha channel is present in `qimg`, it will be dropped in the array representation.

    """

    num_channels = qimg.depth() // 8

    qbits = qimg.bits()
    qbits.setsize(qimg.height() * qimg.width() * num_channels)

    img_bytes = qbits.asstring()

    img_array = np.ascontiguousarray(
        np.frombuffer(img_bytes, dtype=np.uint8).reshape(
            qimg.height(), qimg.width(), -1)[..., 2::-1])

    return img_array

def initiate_feedback_dialog(control, token, channels):
    """ Initiate the feedback dialog box.

    This function grabs a screenshot of the active GUI widget 
    and starts up a feedback dialog box. The dialog box displays a preview of 
    the screenshot, and allows the client-user to enter their name, 
    organization, and a message. This message is then sent to
    the specified Slack channel.

    Parameters
    ----------
    control : `QtGui.QWidget`
        GUI widget whose screenshot will be taken.

    token : str
        Slack API authentication token. 

    channels : list
        List of channels where the message will be sent.

    Note
    ----
    The authentication `token` must bear the required scopes, i.e., it must have 
    permissions to send messages to the specified channels.

    """
    img_data = qimage_to_rgb_array(take_screenshot_qimage(control))

    msg = FeedbackMessage(img_data=img_data, channels=channels, token=token)

    msg_controller = FeedbackController(model=msg)
    msg_controller.configure_traits()


