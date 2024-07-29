from math_logic.logic import main
import multiprocessing
import time
import numpy as np
import sys


if __name__ == '__main__':
    # multiprocessing.set_start_method('spawn')
    # print(np.pi)
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn')
        multiprocessing.freeze_support()
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2 - t1)
    input()