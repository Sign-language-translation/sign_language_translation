import os
import numpy as np
import tensorflow as tf
# Disable any GPU backends (including Metal) so TF runs on CPU only
tf.config.set_visible_devices([], 'GPU')
# Disable XLA JIT compilation
tf.config.optimizer.set_jit(False)

from collections import Counter
import json
from create_database import read_all
from utils.conver_json_to_vector import create_feature_vector
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, ConvLSTM2D, BatchNormalization, Dropout,
    TimeDistributed, Flatten, Dense
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import pickle
import matplotlib
matplotlib.use('Agg')


def save_label_mapping(label_encoder, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"Label encoder saved to {file_path}")


def load_data_from_db():
    vecs, labels = [], []
    for _id, label, category, json_data in read_all():
        try:
            jd = json.loads(json_data)
            vec = create_feature_vector(jd)  # shape: (T, H, W, C) or (T, N, coords)
            vecs.append(vec)
            labels.append(label.split('_')[0])
        except Exception as e:
            print(f"Error ID {_id}: {e}")
    return np.array(vecs, dtype='float32'), labels


def compute_weights(y):
    cw = compute_class_weight('balanced', classes=np.unique(y), y=y)
    return dict(enumerate(cw))


from tensorflow.keras.layers import Reshape, ConvLSTM2D, BatchNormalization, Dropout, Flatten, Dense


def build_convlstm_model(input_shape, num_classes):
    """
    input_shape: (T, N, C) where N=number of joints, C=coordinates per joint
    We'll reshape to (T, 1, N, C) to give ConvLSTM2D a 2D spatial grid of size (1 x N).
    """
    T, N, C = input_shape
    inp = Input(shape=input_shape)  # (T, N, C)

    # Insert a height dimension of 1 so we have a 2D grid: (T, 1, N, C)
    x = Reshape((T, 1, N, C))(inp)  # now ndim=5: (batch, T, 1, N, C)

    # Apply ConvLSTM2D over this “spatial” grid
    x = ConvLSTM2D(
        filters=64,
        kernel_size=(1, 3),  # height=1 so kernel height must be 1
        padding='same',
        return_sequences=False,
        activation='relu'
    )(x)  # output shape: (batch, 1, N, 64)

    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Collapse the remaining spatial dims (1 x N x 64) → vector
    x = Flatten()(x)  # shape: (batch, N*64)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    out = Dense(num_classes, activation='softmax')(x)

    return Model(inputs=inp, outputs=out)
def train_model(model, X_train, y_train, class_weights):
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping('val_loss', patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau('val_loss', factor=0.5, patience=3, min_lr=1e-5),
    ]
    return model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=50,
        batch_size=32,
        class_weight=class_weights,
        callbacks=callbacks
    )


def plot_history(history, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Acc')
    plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.xlabel('Epoch'); plt.ylabel('Accuracy'); plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.xlabel('Epoch'); plt.ylabel('Loss'); plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved training history to {out_path}")


def evaluate_model(model, X_test, y_test, encoder):
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {acc*100:.2f}%")
    preds = np.argmax(model.predict(X_test), axis=-1)
    print(classification_report(y_test, preds, target_names=encoder.classes_))


def create_model(pkl_file_name=None, model_filename=None, models_folder_path="models"):
    # 1. Load and prepare data
    X, labels = load_data_from_db()
    X = np.array(X, dtype='float32')
    encoder = LabelEncoder().fit(labels)
    y = encoder.transform(labels)
    y = np.array(y, dtype='int32')

    # 2. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    # ensure dtypes
    X_train, X_test = X_train.astype('float32'), X_test.astype('float32')
    y_train, y_test = y_train.astype('int32'), y_test.astype('int32')

    print("Train dist:", Counter(y_train), " Test dist:", Counter(y_test))
    class_weights = compute_weights(y_train)

    # 3. Build model
    # Assume X.shape = (samples, T, H, W, C)
    input_shape = X_train.shape[1:]
    num_classes = len(encoder.classes_)
    model = build_convlstm_model(input_shape, num_classes)

    # 4. Train, plot, evaluate
    history = train_model(model, X_train, y_train, class_weights)
    plot_history(history, os.path.join(models_folder_path, "training_history.png"))
    evaluate_model(model, X_test, y_test, encoder)

    # 5. Save encoder & model
    os.makedirs(models_folder_path, exist_ok=True)
    pkl_file_name = pkl_file_name+".pkl" or f"label_encoder_{len(labels) // len(set(labels))}_vpw.pkl"
    save_label_mapping(encoder, os.path.join(models_folder_path, pkl_file_name))
    model_filename = model_filename+".keras" or f"convlstm_rnn_{len(labels) // len(set(labels))}_vpw.keras"
    model.save(os.path.join(models_folder_path, model_filename))
    print(f"Model saved: {model_filename}")


if __name__ == "__main__":
    create_model()