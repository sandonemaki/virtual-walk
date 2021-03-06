import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

from source.nn_models.model import FullModel

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
formatter = logging.Formatter(FORMAT)
logger.setLevel(logging.INFO)

classes = ['walk', 'stand', 'left', 'right']
LR = 5e-5
dropout = 0
layer_struct = [50, 25]
optimizer = 'adam'
batch_size = 50
n_sessions = 1

current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
tb_path = Path(__file__).parents[0].joinpath('logs/{}/'.format(current_time))

data = np.loadtxt('data/training_data.txt', delimiter=',', dtype=object)
X, Y = FullModel.prepare_x_y(data)
# X_scaled = preprocessing.scale(X)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

tb_path_0 = 'logs/'
for i_sess in range(n_sessions):
    print(i_sess)
    tb_path = tb_path_0 + current_time + '_sess_' + str(i_sess)
    cp_path = 'models/' + current_time + '_sess_' + str(i_sess) + '.ckpt'
    try:
        os.mkdir(tb_path)
    except:
        pass
    # try:
    #     os.mkdir(cp_path)
    # except:
    #     pass
    model = FullModel(classes, tensorboard_path=tb_path, lr=LR, n_components=50, layers_NN=layer_struct,
                      dropout=dropout, optimizer=optimizer)
    history = model.train(X_train, Y_train, X_test=X_test, Y_test=Y_test, batch_size=batch_size, epochs=500,
                          callbacks=[tf.keras.callbacks.ModelCheckpoint(filepath='models/weights.hdf5', save_freq=batch_size * 100)], verbose=0)
    model.save_scaler(f'models/scaler_{i_sess}.pkl')
    model.save_PCA(f'models/pca_{i_sess}.pkl')
    model.save_NN(f'models/NN_{i_sess}.h5')
