import glob
import os
import sys

import numpy as np
from astropy.io import fits


class CraneData:

    """
    The data container for crane data.
    """
    def __init__(self, obj_path):
        self.ses_on_data, self.ses_off_data = self.read_on_off_data(obj_path)
        self.freq = self.get_freq(obj_path)

    # TODO: replace os.listdir(obj_path)[1] to be any file in the unhidden dir
    @staticmethod
    def listdir_nohidden(path):
        for f in os.listdir(path):
            if not f.startswith('.'):  #判断是否是隐藏文件（以.开头的排除掉）
                yield f

    @staticmethod
    def get_freq(obj_path):
        try:
            for each_rec in os.listdir(obj_path):
            #for each_rec in os.listdir(os.path.join(obj_path, os.listdir(obj_path))):
                each_rec_path = os.path.join(obj_path, each_rec)
                if os.path.isfile(each_rec_path) and '.fits' in os.path.basename(each_rec_path):
                #os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表。
                # read on data into an array and return
                #each_rec_path = os.path.join(obj_path, os.listdir(obj_path)[each_rec])
                    hdu_list = fits.open(each_rec_path)
                    hdu_data = hdu_list[1].data
                    #freq = hdu_data['SUBFREQ']  # shape(127,4)
                    freq = hdu_data[0].field('DATA')
                    freq1 = freq[:, 0]  # center frequency of first frequency range
                    n_channel = 65536
                    n_rec = 127

                    #delt = hdu_data['CDELT1']
                    delt = 200
                    start = freq1 - delt / 2.
                    stop = freq1 + delt / 2.

                    freq1 = np.linspace(start[0], stop[0], n_channel)  #在指定的间隔内返回均匀间隔的数字
                    break

        except OSError:
            print("Invalid folder input, please check the folder existance. Error msg is ", OSError.message)
            sys.exit()
        print('Get freq finished.')
        return freq1

    @staticmethod
    def read_on_off_data(obj_path):
        """

        :param obj_path:
        :return: shape of (channel,)
        """
        on_data_mean = None
        off_data_mean = None
        n_on_rec = 0.0
        n_off_rec = 0.0
        print('obj_path is', obj_path)
        try:
            for each_session in os.listdir(obj_path):
                #if 'on_tracking' in each_session:      #文件名中包含关键字'on_tracking'
                #for each_rec in os.listdir(os.path.join(obj_path, each_session)):  #'2018-01-28_15-03-24_PegII-UDG23_on_tracking')):
                        # read on data into an array and return
                each_rec_path = os.path.join(obj_path, each_session)
                if os.path.isfile(each_rec_path) and '.fits' in os.path.basename(each_rec_path):    #判断是否是.fit文件
                    hdu_list = fits.open(each_rec_path)
                    hdu_data = hdu_list[1].data
                    data = hdu_data['DATA'].T
                    data = data[0]
                    print(data.shape)
                    each_rec_data_mean = np.mean(data, axis=1)   #取了第0列和最后一列，按行求均值
                    if on_data_mean is None:
                        on_data_mean = each_rec_data_mean
                    else:
                        on_data_mean += each_rec_data_mean
                    n_on_rec += 1.0    #统计个数
                on_data_mean = on_data_mean/n_on_rec   # shape 65536


                #for each_rec in os.listdir(os.path.join(obj_path, each_session)): #'2018-01-28_15-31-37_PegII-UDG23_off_tracking')):
                        # read on data into an array and return
                each_rec_path = os.path.join(obj_path, each_session)
                if os.path.isfile(each_rec_path) and '.fits' in os.path.basename(each_rec_path):
                    hdu_list = fits.open(each_rec_path)
                    hdu_data = hdu_list[1].data
                    data = hdu_data['DATA'].T
                    data = data[0]
                    print(data.shape)
                    each_rec_data_mean = np.mean(data, axis=1)
                    if off_data_mean is None:
                        off_data_mean = each_rec_data_mean
                    else:
                        off_data_mean += each_rec_data_mean
                    n_off_rec += 1.0
                off_data_mean = off_data_mean/n_off_rec

        except OSError:
            print("Invalid folder input, please check the folder existance.")
            sys.exit()
        return on_data_mean, off_data_mean
