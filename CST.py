import numpy as np

class Q_v_state:

    def __init__(self, test):
        self.q = test
        print(self.q)


q = Q_v_state('test')
print(Q_v_state.__setattr__)
#print(q.__dir__())