import numpy as np
import tensorflow as tf
from collections import Counter

import json
from create_database import read_all
from resources.conver_json_to_vector import create_feature_vector
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Dense, LSTM, Dropout, Bidirectional, BatchNormalization,
    Conv1D, Input, GlobalAveragePooling1D
)
from tensorflow.keras.regularizers import l2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt



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

            if vectorized_data.shape != (15000, 3):
                raise ValueError(f"Invalid shape for video {id}: {vectorized_data.shape}")

            vec_lst.append(vectorized_data)
            label_lst.append(label)

        except Exception as e:
            print(f"Error processing data for ID {id}: {e}")
            continue

    return np.array(vec_lst, dtype='float32'), label_lst

# Load and preprocess data
features, labels = load_data_from_db()  # features: (num_videos, 15000, 3)

# Encode labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# # Train-test split
# X_train, X_test, y_train, y_test = train_test_split(
#     features, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
# )

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    features, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
)

# Verify distribution of labels
train_label_distribution = Counter(y_train)
test_label_distribution = Counter(y_test)
print("Train Label Distribution:", train_label_distribution)
print("Test Label Distribution:", test_label_distribution)

# Compute class weights for imbalanced data
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(class_weights))

# Learning rate scheduler
def lr_scheduler(epoch, lr):
    return lr * tf.math.exp(-0.05) if epoch >= 10 else lr

# Build the model
def create_model(input_shape, num_classes):
    input_layer = Input(shape=input_shape)

    # Convolutional layer
    x = Conv1D(64, kernel_size=3, activation='relu')(input_layer)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Bidirectional LSTM
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Global Average Pooling
    x = GlobalAveragePooling1D()(x)

    # Fully connected layer
    x = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Output layer
    output_layer = Dense(num_classes, activation='softmax')(x)

    return Model(inputs=input_layer, outputs=output_layer)

# Create and compile the model
model = create_model(input_shape=(15000, 3), num_classes=len(label_encoder.classes_))
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Custom callback to print progress
class CustomCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        print(f"Epoch {epoch + 1}: Loss={logs['loss']:.4f}, Accuracy={logs['accuracy']:.4f}, "
              f"Val Loss={logs['val_loss']:.4f}, Val Accuracy={logs['val_accuracy']:.4f}")

# Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-5),
    tf.keras.callbacks.LearningRateScheduler(lr_scheduler),
    CustomCallback()
]

# Train the model
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=callbacks,
    class_weight=class_weights
)

# Evaluate the model
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")

# Generate predictions and classification report
y_pred = np.argmax(model.predict(X_test), axis=-1)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save the model
model.save('sign_language_video_model.h5')
print("Model saved as 'sign_language_video_model.h5'.")

# Plot learning curves
plt.figure(figsize=(14, 6))

# Loss plot
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# Accuracy plot
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()
plt.show()