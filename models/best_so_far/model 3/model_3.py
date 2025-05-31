import os
import json
import pickle
import numpy as np
import tensorflow as tf
from collections import Counter
from create_database import read_all
from utils.conver_json_to_vector import create_feature_vector
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv2D, Conv1D, Reshape, BatchNormalization, MaxPooling2D, MaxPooling1D,
    TimeDistributed, Flatten, Bidirectional, GRU,
    LayerNormalization, Dense, Dropout, Add, Layer
)
from tensorflow.keras.layers import MultiHeadAttention
from tensorflow.keras.layers import GlobalAveragePooling1D
from tensorflow.keras import regularizers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


def save_label_mapping(label_encoder, file_path):
    """Save the label encoder to a file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"Label encoder saved to {file_path}")


def compute_weights(y_train):
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    return dict(enumerate(class_weights))


class SelfAttention(Layer):
    """
    Simple self-attention over time dimension.
    Input shape: (batch, time, features)
    Output shape: (batch, features)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(
            shape=(input_shape[-1], input_shape[-1]),
            initializer='glorot_uniform', trainable=True, name='W_attn'
        )
        self.b = self.add_weight(
            shape=(input_shape[-1],),
            initializer='zeros', trainable=True, name='b_attn'
        )
        self.u = self.add_weight(
            shape=(input_shape[-1],),
            initializer='glorot_uniform', trainable=True, name='u_attn'
        )
        super().build(input_shape)

    def call(self, inputs):
        # inputs: (batch, T, F)
        u_it = tf.tanh(tf.tensordot(inputs, self.W, axes=[2,0]) + self.b)
        scores = tf.tensordot(u_it, self.u, axes=[2,0])       # (batch, T)
        alphas = tf.nn.softmax(scores, axis=1)                # (batch, T)
        context = tf.matmul(tf.expand_dims(alphas, 1), inputs)  # (batch,1,F)
        return tf.squeeze(context, 1)                         # (batch, F)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[2])


def build_3dcnn_rnn_with_attention(input_shape, num_classes):
    """
    input_shape = (frames, height, width, channels)
    """
    inp = Input(shape=input_shape)
    # if input is 3D (frames, features, channels), reshape and use Conv1D
    if len(input_shape) == 3:
        # input_shape = (frames, features, channels)
        # Merge features and channels per time step
        x = Reshape((input_shape[0], input_shape[1] * input_shape[2]))(inp)  # (batch, T, features*C)
        # 1D convolutions over time dimension
        x = Conv1D(64, kernel_size=3, padding='same', activation='swish',
                   kernel_regularizer=regularizers.l2(1e-4))(x)
        x = BatchNormalization()(x)
        x = MaxPooling1D(pool_size=2)(x)  # reduce time dimension by 2
        x = Conv1D(128, kernel_size=3, padding='same', activation='swish',
                   kernel_regularizer=regularizers.l2(1e-4))(x)
        x = BatchNormalization()(x)
        x = MaxPooling1D(pool_size=2)(x)  # further reduce time
    else:
        # original richer spatial encoder
        x = TimeDistributed(Conv2D(32, 3, padding='same',
            activation='relu',
            kernel_regularizer=regularizers.l2(1e-4)))(inp)
        x = TimeDistributed(BatchNormalization())(x)
        x = TimeDistributed(MaxPooling2D(2))(x)

        x = TimeDistributed(Conv2D(64, 3, padding='same',
            activation='swish',
            kernel_regularizer=regularizers.l2(1e-4)))(x)
        x = TimeDistributed(BatchNormalization())(x)
        x = TimeDistributed(MaxPooling2D(2))(x)

        # flatten spatial dims
        x = TimeDistributed(Flatten())(x)  # (batch, T, feats)

    # temporal encoder (bidirectional GRU instead of LSTM)
    x = Bidirectional(GRU(64, return_sequences=True))(x)
    x = LayerNormalization()(x)
    x = Dropout(0.3)(x)

    # multi-head self-attention
    attn = MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization()(x)
    x = Dropout(0.3)(x)

    # pool across time
    x = GlobalAveragePooling1D()(x)

    # final MLP
    x = Dense(128, activation='relu',
              kernel_regularizer=regularizers.l2(1e-4))(x)
    x = Dropout(0.3)(x)
    out = Dense(num_classes, activation='softmax')(x)

    return Model(inp, out)


def train_model(model, X_train, y_train, class_weights):
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=3, min_lr=1e-5
        ),
    ]

    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=100,
        batch_size=32,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=2
    )

    # plot
    plt.figure(figsize=(14,6))
    plt.subplot(1,2,1)
    plt.plot(history.history['accuracy'], label='train acc')
    plt.plot(history.history['val_accuracy'], label='val acc')
    plt.legend(); plt.title('Accuracy')

    plt.subplot(1,2,2)
    plt.plot(history.history['loss'], label='train loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.legend(); plt.title('Loss')

    plt.tight_layout()
    plt.savefig("training_history_attention.png")
    return history


def evaluate_model(model, X_test, y_test, label_encoder):
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {acc*100:.2f}%")
    y_pred = np.argmax(model.predict(X_test, verbose=0), axis=-1)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))


def load_data_from_db():
    """Load JSON from DB → feature matrix (frames, H, W, C)."""
    vecs, labels = [], []
    for idx, label, cat, json_data in read_all():
        try:
            d = json.loads(json_data)
            mat = create_feature_vector(d)
            vecs.append(mat)
            labels.append(label.split("_")[0])
        except Exception as e:
            print(f"Error {idx}: {e}")
    return np.array(vecs, dtype='float32'), labels


def create_model(pkl_file_name=None, model_filename=None, models_folder_path="models/local_models"):
    # 1) data
    X, labels = load_data_from_db()
    encoder = LabelEncoder().fit(labels)
    y = encoder.transform(labels)

    # 2) split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Train dist:", Counter(y_train), " Test dist:", Counter(y_test))
    class_weights = compute_weights(y_train)

    # 3) build
    input_shape = X_train.shape[1:]
    num_classes = len(encoder.classes_)
    model = build_3dcnn_rnn_with_attention(input_shape, num_classes)
    model.summary()

    # 4) train
    history = train_model(model, X_train, y_train, class_weights)

    # 5) eval
    evaluate_model(model, X_test, y_test, encoder)

    # 6) save
    os.makedirs(models_folder_path, exist_ok=True)
    pkl_file_name = pkl_file_name or f"label_attn_{len(labels)//num_classes}_vpw.pkl"
    model_filename = model_filename or f"attn_on_{len(labels)//num_classes}_vpw.keras"

    save_label_mapping(encoder, os.path.join(models_folder_path, pkl_file_name))
    model.save(os.path.join(models_folder_path, model_filename))
    print(f"Saved model → {model_filename}")


if __name__ == "__main__":
    create_model()