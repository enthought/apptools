# Author: Prabhu Ramachandran <prabhu [at] aero . iitb . ac . in>
# Copyright (c) 2008,  Prabhu Ramachandran
# License: BSD Style.

import re

# This code is copied from enthought.tvtk.common.  We do this to avoid
# any dependency on enthought.tvtk.

class _Camel2Enthought:
    """Simple functor class to convert names from CamelCase to
    Enthought compatible names.

    For example::
      >>> camel2enthought = _Camel2Enthought()
      >>> camel2enthought('XMLActor2DToSGML')
      'xml_actor2d_to_sgml'
      
    """
    
    def __init__(self):
        self.patn = re.compile(r'([A-Z0-9]+)([a-z0-9]*)')
        self.nd_patn = re.compile(r'(\D[123])_D')
    def __call__(self, name):
        ret = self.patn.sub(self._repl, name)
        ret = self.nd_patn.sub(r'\1d', ret)
        if ret[0] == '_':
            ret = ret[1:]
        return ret.lower()    
    def _repl(self, m):
        g1 = m.group(1)
        g2 = m.group(2)
        if len(g1) > 1:
            if g2:
                return '_' + g1[:-1] + '_' + g1[-1] + g2
            else:
                return '_' + g1
        else:
            return '_' + g1 + g2

# Instantiate a converter.
camel2enthought = _Camel2Enthought()

