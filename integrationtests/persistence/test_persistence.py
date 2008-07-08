class Foo0:
    """ The original class written with no expectation of being upgraded """
    def __init__(self):
        self.prenom = 'didier'
        self.surnom = 'enfant'
        

class Foo1:
    """ Now to handle both Foo v0 and Foo v1 we need to add more code ..."""
    
    def __init__(self, firstname, lastname):
        """ This does not get called when the class is unpickled."""
        self.firstname = firstname
        self.lastname = lastname
        
        
class Foo:
        
    def __str__(self):
        result = ['-----------------------------------------------------------']
        keys = dir(self)
        for key in keys:
             result.append('%s ---> %s' % (key, getattr(self, key)))
        result.append('-----------------------------------------------------------')     
        return '\n'.join(result)
        
    def __setstate__(self, state):
        print 'calling setstate on the real Foo'
        state['set'] = True
        self.__dict__.update(state)

        

def save(fname, str):
    f=open(fname, 'w')
    f.write(str)
    f.close()  
    return         
        
    
if __name__ == '__main__':
    
    # Create dummy test data .......
    #from cStringIO import StringIO
    import pickle
    
    obj = Foo0() 
    print obj
    t0 = pickle.dumps(obj) #.replace('Foo0', 'Foo')
    save('foo0.txt', t0)
    
    '''obj = Foo1('duncan', 'child')
    t1 = pickle.dumps(obj).replace('Foo1', 'Foo')
    save('foo1.txt', t1)
    
    obj = Foo2('duncan child')
    t2 = pickle.dumps(obj).replace('Foo2', 'Foo')
    save('foo2.txt', t2)
    
    obj = Foo3('duncan child')
    t3 = pickle.dumps(obj).replace('Foo3', 'Foo')
    save('foo3.txt', t3)
    '''
    
    print '===================================================================='

    from enthought.persistence.versioned_unpickler import VersionedUnpickler
    from update1 import Update1
    # Try and read them back in ...
    f = open('foo0.txt')
    
    import sys 
    rev = 1
    __import__('integrationtests.persistence.update%d' % rev)
    mod = sys.modules['integrationtests.persistence.update%d' % rev]
    klass = getattr(mod, 'Update%d' % rev)
    updater = klass()
    print '%s %s' % (rev, updater)           
    
    p = VersionedUnpickler(f, updater).load()
    print p
    print 'Restored version %s %s' % (p.lastname, p.firstname)
    #print p.set
  
               