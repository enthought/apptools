This package provides tools and graphical editor for working with ReStructured
Text.

To use the editor, run 'python app.py'. 

Non-Windows users should use the Qt Traits UI backend if possible, because the
builtin wxWidgets HTML renderer is very poor. Windows users can use either
backend; in the wxWidgets backend, Internet Explorer is used to render the
HTML. To specify the backend, set the ETS_TOOLKIT environment variable to either
'wx' or 'qt4'.
