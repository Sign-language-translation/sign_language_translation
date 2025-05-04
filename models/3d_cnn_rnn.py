import numpy as np
import tensorflow as tf
from collections import Counter
import json
from create_database import read_all
from resources.conver_json_to_vector import create_feature_vector
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Dense, LSTM, Dropout, Bidirectional, BatchNormalization,
    Input, TimeDistributed, Flatten
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Conv2D, MaxPooling2D
import pickle




def save_label_mapping(label_encoder, file_path):
    """Save the label encoder to a file."""
    with open(file_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"Label encoder saved to {file_path}")




# Function to load data from the database and create feature vectors
def load_data_from_db():
    """Load data from the database and transform JSON content into feature vectors."""
    vec_lst, label_lst = [], []
    not_processed_data = read_all()

    for id, label, category, json_data in not_processed_data:
        try:
            # Parse the JSON content into a dictionary
            json_dict = json.loads(json_data)

            # Create feature vector of shape (15000, 3)
            vectorized_data = create_feature_vector(json_dict)

            # if vectorized_data.shape != (15000, 3):
            #     raise ValueError(f"Invalid shape for video {id}: {vectorized_data.shape}")

            vec_lst.append(vectorized_data)
            label_lst.append(label)

        except Exception as e:
            print(f"Error processing data for ID {id}: {e}")
            continue
    for i in range(len(label_lst)):
        label_lst[i] = label_lst[i].split("_")[0]
    return np.array(vec_lst, dtype='float32'), label_lst

def compute_weights(y_train):
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    return dict(enumerate(class_weights))


def build_3dcnn_rnn_model(input_shape, num_classes):
    input_layer = Input(shape=input_shape)

    # 2D Convolutional Layer
    x = Conv2D(64, kernel_size=(3, 3), activation='relu')(input_layer)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    # Flatten spatial dimensions while keeping the temporal dimension
    x = TimeDistributed(Flatten())(x)

    # Pass to LSTM
    x = Bidirectional(LSTM(64, return_sequences=False))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Fully Connected Layer
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)

    # Output Layer
    output_layer = Dense(num_classes, activation='softmax')(x)

    return Model(inputs=input_layer, outputs=output_layer)


def train_model(model, X_train, y_train, class_weights):
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-5)
    ]

    history = model.fit(
        X_train, y_train,
        validation_split=0.2,
        epochs=50,
        batch_size=32,
        class_weight=class_weights,
        callbacks=callbacks
    )

    # Plot training and validation accuracy
    plt.figure(figsize=(14, 6))

    # Accuracy plot
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # Loss plot
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.show()

    return history

def evaluate_model(model, X_test, y_test, label_encoder):
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

    y_pred = np.argmax(model.predict(X_test), axis=-1)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

def main():
    features, labels = load_data_from_db()
    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    save_label_mapping(label_encoder, f'label_encoder_3d_rnn_cnn_{ len(labels) // len(set(labels))}_vpw.pkl')


    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        features, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
    )

    # Verify distribution of labels
    train_label_distribution = Counter(y_train)
    test_label_distribution = Counter(y_test)
    print("Train Label Distribution:", train_label_distribution)
    print("Test Label Distribution:", test_label_distribution)

    # Compute class weights
    class_weights = compute_weights(y_train)

    # Step 3: Build the model
    input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3])  # (50, 75, 3)
    num_classes = len(label_encoder.classes_)
    model = build_3dcnn_rnn_model(input_shape, num_classes)

    # Step 4: Train the model
    history = train_model(model, X_train, y_train, class_weights)

    # Step 5: Evaluate the model
    evaluate_model(model, X_test, y_test, label_encoder)

    # Save the model with a descriptive filename based on videos per word (vpw)
    videos_per_word = len(labels) // len(set(labels))
    model_filename = f'3d_rnn_cnn_on_{videos_per_word}_vpw.keras'
    model.save(model_filename)

    print(f"Model saved as '{model_filename}'.")

main()
