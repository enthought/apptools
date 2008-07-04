# Update class names from the immediately prior version only
# to ensure that cycles are not possible 

from enthought.persistence.updater import Updater
        

def update_project(self, state):
    print 'updating to v3'
    metadata = state['metadata']
    metadata['version'] = 3
    metadata['finished'] = True
    return state

class Update3(Updater):

    def __init__(self):
    
        self.refactorings = {
            ("__main__", "Foo1"): ("__main__", "Foo2"),
        }
        
        self.setstates = {
            ("cplab.project", "Project"):  update_project
        }
            