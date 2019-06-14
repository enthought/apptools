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
     control: TODO     

     Returns:
     --------
     qimg: PyQt4.QtGui.QImage
        Screenshot image as PyQt4.QtGui.QImage instance. 

     """

    return QPixmap.grabWidget(control).toImage()

def qimage_to_pillow(qimg, fmt='PNG'):

    qbuf = QBuffer()
    qbuf.open(QBuffer.WriteOnly)
    qimg.save(qbuf, fmt)

    return Image.open(io.BytesIO(qbuf.data()))

def initiate_feedback_dialog(control, token, channels):

    img_data = np.array(
            qimage_to_pillow(take_screenshot_qimage(control)))[..., :3]

    msg = FeedbackMessage(img_data=img_data, channels=channels, token=token)

    msg_controller = FeedbackController(model=msg)
    msg_controller.configure_traits()


