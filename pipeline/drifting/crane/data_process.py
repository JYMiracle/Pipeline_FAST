import os
from level1 import *
from load_data import CraneData
from plot import *


class CraneDataProcessTask:

    """
    This class is the frame to use different modules and process data.
    Detailed functions (such as loading data, plot and processing) are not included in this class.
    """

    def __init__(self, obj_name, bsl_flag, smooth_box, polyfit_deg):
        """
        Parameters and methods needed for data processing.

        :param obj_name: type string, the object name.
        :param bsl_flag: type boolean, the flag for doing baseline or not.
        :param smooth_box: type int, the width of smooth box.
        :param polyfit_deg: type int, poly fitting degree. 
        """
        self.bsl_flag = bsl_flag    #是否做baseline
        self.smooth_box = smooth_box   #smooth_box宽度
        self.polyfit_deg = polyfit_deg   #拟合程度

        self.obj_name = obj_name
        obj_path = os.path.join(os.path.dirname(os.getcwd()), 'test_data', obj_name)

        crane_data = CraneData(obj_path)
        # self.data = crane_data.data
        self.ses_on_data = crane_data.ses_on_data  # [n_channel]
        self.ses_off_data = crane_data.ses_off_data

        self.n_channel = self.ses_on_data.shape     #频道数就等于on的长度

        self.freq = crane_data.freq                 #频率就等于crane_data的频率

        self.ses_on_data_bdp = None
        self.ses_off_data_bdp = None
        self.sessions_mean = None

    # TODO: save the intermediate data
    def level1_process(self):
        """
        Level I processing for loaded data
        :return ON, OFF and mean(ON-OFF) data after bandpass for each record
        """

        each_ses_on_bdp = bdp_correction(self.ses_on_data, self.freq, self.polyfit_deg)
        each_ses_off_bdp = bdp_correction(self.ses_off_data, self.freq, self.polyfit_deg)

        ses_on_data_bdp = np.mean(each_ses_on_bdp, axis=1)

        ses_off_data_bdp = np.mean(each_ses_off_bdp, axis=1)

        # array shape different for one session and multiple sessions
        sessions_mean = (ses_on_data_bdp - ses_off_data_bdp)     #平均值

        self.ses_on_data_bdp = ses_on_data_bdp
        self.ses_off_data_bdp = ses_off_data_bdp
        self.sessions_mean = sessions_mean

    def subtract_bandpass(self):
        """
        Subtract a part of spectra on left and right to remove instrument effect, before baseline.
        The percentage is set to 18% for testing stage, will adjust and fix in the future.
        :return:
        """
        start_i = int(len(self.freq) * 0.18)
        end_i = int(len(self.freq) * 0.82)
        plot_substract(self.freq, self.ses_on_data-self.ses_off_data, self.freq[start_i], self.freq[end_i])
        self.freq = self.freq[start_i:end_i]
        self.ses_on_data = self.ses_on_data[start_i:end_i]
        self.ses_off_data = self.ses_off_data[start_i:end_i]

    def plot_result(self):
        """
        Level processing for loaded data
        """
        plot_mean_sessions(self.freq, self.sessions_mean, self.smooth_box, self.bsl_flag, self.polyfit_deg)

    def get_session_num(self):
        """
        :return: session number from data shape [n_channel, n_record, *n_sec]
        """
        if len(self.ses_on_data.shape) == 2:
            return 1
        else:
            return self.ses_on_data.shape[2]
