# Update class names from the immediately prior version only
# to ensure that cycles are not possible 

from enthought.persistence.updater import Updater

def cleanup_foo(self, state):
    
    print 'cleaning up Foo0'  
    state['firstname'] = state['prenom']
    state['lastname'] = state['surnom']
                
    del state['prenom']
    del state['surnom']  
    
    '''for key in state:
        print '%s state ---> %s' % (key, state[key])
    '''
    
    #self.__setstate_original__(state)       
    self.__dict__.update(state)
    
    
def update_project(self, state):
    print 'updating to v1'
    metadata = state['metadata']
    metadata['version'] = 1
    metadata['diesel'] = 'E300TD'
    return state
        

class Update1(Updater):

    def __init__(self):
    
        self.refactorings = {
            ("__main__", "Foo0"): ("__main__", "Foo"),
        }
        
        self.setstates = {
            ("cplab.project", "Project"):  update_project  
        }
            