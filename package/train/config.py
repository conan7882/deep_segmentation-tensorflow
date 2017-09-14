import scipy.misc
import os
import numpy as np

from ..dataflow.base import DataFlow

__all__ = ['TrainConfig']

def assert_type(v, tp):
    assert isinstance(v, tp), "Expect " + str(tp) + ", but " + str(v.__class__) + " is given!"

class TrainConfig(object):
    def __init__(self, 
                 dataflow = None, model = None,
                 batch_size = 1, max_epoch = 100):

        assert dataflow is not None, "dataflow cannot be None!"
        self.dataflow = dataflow
        assert_type(self.dataflow, DataFlow)

        self.batch_size = batch_size
        self.max_epoch = max_epoch
        assert self.batch_size > 0 and self.max_epoch > 0

        


from ..dataflow.dataset.BSDS500 import BSDS500
if __name__ == '__main__':
    
    a = BSDS500('val','D:\\Qian\\Dataset\\Segmentation\\BSR_bsds500\\BSR\\BSDS500\\data\\')
    # print(a.epochs_completed)
    t = TrainConfig(a,0)

