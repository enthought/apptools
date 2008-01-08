# Standard library imports
from pickle import *
import sys, new
import logging

# Enthought library imports
from enthought.persistence.updater import __replacement_setstate__


logger = logging.getLogger(__name__)


class VersionedUnpickler(Unpickler):
    """ This class reads in a pickled file created at revision version 'n'
    and then applies the transforms specified in the updater class to 
    generate a new set of objects which are at revision version 'n+1'.
    
    I decided to keep the loading of the updater out of this generic class
    because we will want updaters to be generated for each plugin's type
    of project. eg ProAVA2 projects will need different updaters to the 
    ProAct project. 
    
    This ensures that the VersionedUnpickler can remain ignorant about the
    actual version numbers - all it needs to do is upgrade one release.  
    """

    
    def __init__(self, file, updater=None):
        Unpickler.__init__(self, file)
        self.updater = updater
        return
                      
    
    def find_class(self, module, name):
        """ Overridden method from Unpickler. 
        
        NB  __setstate__ is not called until later.
        """

        if self.updater:
            # check to see if this class needs to be mapped to a new class
            # or module name    
            original_module, original_name  = module, name
            #logger.debug('omodule:%s oname:%s' % (original_module, original_name))
            module, name = self.updater.get_latest(module, name)
            #logger.debug('module:%s name:%s' % (module, name))
           
            # load the class...
            '''__import__(module)
            mod = sys.modules[module]
            klass = getattr(mod, name)'''
            klass = self.import_name(module, name)
            
            # add the updater....  TODO - why the old name? 
            self.add_updater(original_module, original_name, klass)
            
        else:
            # there is no updater so we will be reading in an up to date 
            # version of the file...
            try:
                klass = Unpickler.find_class(self, module, name)
            except:
                logger.error("Looking for [%s] [%s]" % (module, name))
                logger.exception('Problem using default unpickle functionality')
            
            # restore the original __setstate__ if necessary
            fn = getattr(klass, '__setstate_original__', False)
            if fn:
                m = new.instancemethod(fn, None, klass)
                setattr(klass, '__setstate__', m)
           
        return klass   
        

    def add_updater(self, module, name, klass):
        """ If there is an updater defined for this class we will add it to the
        class as the __setstate__ method.
        """       
          
        fn = self.updater.setstates.get((module, name), False)       
        
        if fn:
            # move the existing __setstate__ out of the way
            self.backup_setstate(module, klass)
            
            # add the updater into the class 
            m = new.instancemethod(fn, None, klass)
            setattr(klass, '__updater__', m)
            
            # hook up our __setstate__ which updates self.__dict__
            m = new.instancemethod(__replacement_setstate__, None, klass)
            setattr(klass, '__setstate__', m)

        else:
            pass
            #print 'No updater fn to worry about'
        
        return
        

    def backup_setstate(self, module, klass):
        """ If the class has a user defined __setstate__ we back it up.
        """
        if getattr(klass, '__setstate__', False):
            
            if getattr(klass, '__setstate_original__', False):
                # don't overwrite the original __setstate__
                name = '__setstate__%s' % self.updater.__class__
            else:
                # backup the original __setstate__ which we will restore
                # and run later when we have finished updating the class 
                name = '__setstate_original__'
            
            #logger.debug('renaming __setstate__ to %s' % name)    
            method = getattr(klass, '__setstate__')
            m = new.instancemethod(method, None, klass)
            setattr(klass, name, m)
            
        else:
            # the class has no __setstate__ method so do nothing
            pass
            
        return

        
    def import_name(self, module, name):
        """ 
        If the class is needed for the latest version of the application then
        it should presumably exist. 
        
        If the class no longer exists then we should perhaps return 
        a proxy of the class. 
        
        If the persisted file is at v1 say and the application is at v3 then 
        objects that are required for v1 and v2 do not have to exist they only 
        need to be placeholders for the state during an upgrade. 
        """
        #print "importing %s %s" % (name, module)
        module = __import__(module, globals(), locals(), [name])
        return vars(module)[name]
        
### EOF #################################################################
           
   