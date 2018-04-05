import os

dataset_path = './data'

output_path = './output'
if not os.path.exists(output_path):
    os.makedirs(output_path)


common_cols = ['year', 'month', 'season']

data_config_dict = {'beijing' : ('BeijingPM20100101_20151231.csv',
                                ['Dongsi', 'Dongsihuan', 'Nongzhanguan']),
                    'chengdu' : ('ChengduPM20100101_20151231.csv',
                                ['Caotangsi', 'Shahepu']),
                    'guangzhou' : ('GuangzhouPM20100101_20151231.csv',
                                ['City Station', '5th Middle School']),
                    'shanghai' : ('ShanghaiPM20100101_20151231.csv',
                                ['Jingan', 'Xuhui']),
                    'shenyang' : ('ShenyangPM20100101_20151231.csv',
                                ['Taiyuanjie', 'Xiaoheyan'])

}
