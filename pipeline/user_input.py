import os
import subprocess
import config_properties


class UserInput:
    def __init__(self):
        self.obs_mode = None   #观测模式 1,2
        self.instrument = None  #仪器 1,2
        self.obj_name = None   #数据名（路径）
        self.smooth_box = None
        self.bsl_flag = None
        self.freq = None
        self.user_init_input()

    def user_init_input(self):

        # Get user input for obs mode and other interactive
        try:
            self.obs_mode = int(input('Please choose your observation mode \n [1 - Drifting 2 - Tracking]'))   #drifting 扫描  tracking 追踪；目前改追踪部分
        except TypeError:
            print('Selection out of options range! Please choose 1 or 2.')

        self.instrument = int(input('Please choose your instrument option \n [1 - Spectrometer 2 - Crane]'))

        # Choose load data from local or remote
        local_or_remote = input('Load data from local or remote? [l/r]')
        cwd = os.getcwd()

        if local_or_remote == 'l':
            # local
            self.obj_name = input('Please type folder name: ')
            obj_path = os.path.join(os.path.dirname(cwd), 'test_data', self.obj_name)
            if not os.path.exists(obj_path):
                print("Not valid object name, check config_properties.py!")
                exit(0)
            # Get spectrometer data freq from remote .m file, set in properties
            if self.instrument == 1:
                ssh = open(os.path.join(os.path.dirname(cwd), 'test_data', self.obj_name, 'b51_get_spec_HI_RF.m'), 'r')
                for line in ssh.readlines():    #由此处可以推断出 b51_get_spec_HI_RF.m 里面有三个变量，fa  fb  npt
                    if 'fa =' in line:
                        fa = line.split()  # do stuff
                    if 'fb =' in line:
                        fb = line.split()
                    if 'npt =' in line:
                        npt = line.split()
                self.freq = [fa[2][:-1], fb[2][:-1]]   #获取成它的频率
                # tick_num = npt[2][:-1]
                print('self.freq is', self.freq)

        if local_or_remote == 'r':
            # TODO: change this part to fully get data from remote
            # Get data object name from properties setting and check whether the file exists locally
            if self.instrument == 1:
                self.obj_name = config_properties.SPEC_DATA_OBJECT
            if self.instrument == 2:
                self.obj_name = config_properties.CRANE_DATA_OBJECT

            obj_path = os.path.join(os.path.dirname(cwd), 'test_data', self.obj_name)
            if not os.path.exists(obj_path):
                print("Not valid object name, check config_properties.py!")
                exit(0)

            # Get spectrometer data freq from remote .m file, set in properties
            if self.instrument == 1:
                ssh = subprocess.Popen(
                    ['ssh', '-p 33322', config_properties.REMOTE, 'cat', config_properties.FREQ_FILE],
                    stdout=subprocess.PIPE)
                for line in ssh.stdout:
                    if 'fa =' in line:
                        fa = line.split()  # do stuff
                    if 'fb =' in line:
                        fb = line.split()
                    if 'npt =' in line:
                        npt = line.split()
                self.freq = [fa[2][:-1], fb[2][:-1]]
                # tick_num = npt[2][:-1]
                print('self.freq is', self.freq)

        # Smooth box width for final result
        self.smooth_box = input('Please type the smoothing width of the boxcar' +
                                    'average: [10]') or 10

        # Baseline or not
        self.bsl_flag = True
        if input('Baseline the result? [y/n] default as yes').lower() == 'n':
            self.bsl_flag = False

    @staticmethod
    def prompt_poly_fit():
        poly_fit = input('Fitting result acceptable? (default fitting degree as 1) \n'
                             'If yes, please type 0, otherwise type the new fitting degree num: ')
        if int(poly_fit) > 2:
            if input('Polyfit degree > 2 may decrease the performance, you sure? [yes/no]') == 'no':
                print('Poly fitting degree is 2')
                return 2
        return int(poly_fit)
