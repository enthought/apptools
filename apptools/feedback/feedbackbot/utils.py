""" 
This module provides some helper functions for the feedback plugin. These
functions are designed to be used by the user-developer so that the feedback
plugin can be used in their application. 
"""

from PyQt4.QtGui import QPixmap

def take_screenshot_qimg(info):
    """ Take screenshot of an active GUI widget. 

     Parameters
     ----------
     info: traitsui.UIInfo
         The UIInfo instance which contains the active widget.
     
     Returns:
     --------
     qimg: PyQt4.QtGui.QImage
        Screenshot image as PyQt4.QtGui.Qimage instance. 

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

