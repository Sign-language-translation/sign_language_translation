import os
import numpy as np
import json
import pickle
from tensorflow.keras.models import load_model
from keras.models import Model
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from model_5 import SelfAttention
from datetime import datetime

# Paths
MODEL_FILE_PATH = 'model-5_14000_vpw.keras'
LABEL_ENCODER_FILE_PATH = 'label_encoder_model-5_14000_vpw.pkl'
JSON_DIR = '../resources/motion_data'

# Load model and label encoder

model = load_model(MODEL_FILE_PATH, custom_objects={'SelfAttention': SelfAttention})
with open(LABEL_ENCODER_FILE_PATH, 'rb') as f:
    label_encoder = pickle.load(f)

# Extract embeddings from intermediate layer
embedding_model = Model(inputs=model.input, outputs=model.layers[-2].output)

def flatten_landmarks(landmarks, expected_points):
    flat = []
    for i in range(expected_points):
        if i < len(landmarks):
            point = landmarks[i]
            x = point.get("x", 0.0)
            y = point.get("y", 0.0)
            z = point.get("z", 0.0)
            v = point.get("visibility", 0.0)
            flat.extend([x, y, z, v])
        else:
            flat.extend([0.0, 0.0, 0.0, 0.0])
    return flat

def load_mediapipe_json(json_path):
    print(f'Loading {json_path}')
    with open(json_path, 'r') as f:
        data = json.load(f)

    sequence = []
    for frame in data:
        keypoints = []

        # Pose
        pose = frame.get("pose", [])
        keypoints.extend(flatten_landmarks(pose, 33))  # 33 x 4

        # Hands (2 × 21 x 4)
        hands = frame.get("hands", [])
        for i in range(2):
            if i < len(hands):
                hand = hands[i]
            else:
                hand = []
            keypoints.extend(flatten_landmarks(hand, 21))

        sequence.append(keypoints)

    # Pad or trim to 150 frames
    while len(sequence) < 150:
        sequence.append([0.0] * 300)  # pad with zeros
    if len(sequence) > 150:
        sequence = sequence[:150]  # trim to 150

    # Reshape: (150, 75, 4) → drop 'visibility' to get (150, 75, 3)
    sequence = np.array(sequence).reshape((150, 75, 4))[:, :, :3]
    return sequence

def main():
    # Hebrew translations for word labels
    label_translation = {
        'hello': 'שלום', 'thanks': 'תודה', 'need': 'צריך', 'now': 'עכשיו', 'when': 'מתי',
        'why': 'למה', 'appointment': 'תור', 'schedule': 'לקבוע', 'arrive': 'להגיע', 'station': 'תחנה',
        'bus': 'אוטובוס', 'phone': 'טלפון', 'place': 'מקום', 'help': 'לעזור', 'name': 'שם',
        'no': 'לא', 'go': 'ללכת', 'come': 'לבוא', 'I': 'אני', 'you': 'אתה', 'home': 'בית',
        'ticket': 'כרטיס', 'later': 'אחר כך', 'doctor': 'רופא', 'idCard': 'תעודת זהות',
        'ambulance': 'אמבולנס', 'clinic': 'קופת חולים'
    }


    # Load all samples
    embeddings = []
    labels = []
    # MAX_SAMPLES = 500*2
    count = 0
    for root, _, files in os.walk(JSON_DIR):
        for file in files:
            if file.endswith('.json'):
                sequence = load_mediapipe_json(os.path.join(root, file))
                if sequence is not None:
                    vec = np.expand_dims(sequence, axis=0)  # (1, 150, 75, 3)
                    emb = embedding_model.predict(vec, verbose=0)
                    embeddings.append(emb[0])
                    label = file.split('_')[0]
                    labels.append(label)

        #             count += 1
        #             if count >= MAX_SAMPLES:
        #                 print(f"🔹 Reached {MAX_SAMPLES} samples, stopping early for debug")
        #                 break
        # if count >= MAX_SAMPLES:
        #     break

    # Convert to array
    X = np.array(embeddings)
    label_ids = label_encoder.transform(labels)

    # Clustering
    kmeans = KMeans(n_clusters=10, random_state=42)
    cluster_ids = kmeans.fit_predict(X)

    # Visualize with t-SNE
    X_tsne = TSNE(n_components=2, perplexity=20).fit_transform(X)

    plt.figure(figsize=(16, 10))

    for label in sorted(set(labels)):
        idxs = [i for i, l in enumerate(labels) if l == label]

        hebrew_label = label_translation.get(label, label)  # fallback to original if missing
        hebrew_label = hebrew_label[::-1]
        plt.scatter(X_tsne[idxs, 0], X_tsne[idxs, 1], s=10, label=hebrew_label, alpha=0.8)

        x_mean = np.mean(X_tsne[idxs, 0])
        y_mean = np.mean(X_tsne[idxs, 1])
        plt.text(
            x_mean, y_mean, hebrew_label,  # reverse the string manually
            fontsize=14, fontweight='bold', ha='center', va='center',
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.3')
        )

    plt.title('t-SNE of Sign Language Gestures', fontsize=16)
    plt.xlabel('t-SNE 1', fontsize=14)
    plt.ylabel('t-SNE 2', fontsize=14)
    plt.grid(True)

    # Move legend outside plot
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, ncol=1, title="Words", title_fontsize=16)
    plt.tight_layout()

    # Save plot with timestamp
    # Create output folder if it doesn't exist
    output_dir = "cluster_plots"
    os.makedirs(output_dir, exist_ok=True)

    # Count unique words
    num_words = len(set(labels))

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"tsne_plot_{num_words}_words_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    # Save plot
    plt.savefig(filepath)
    print(f"✅ Plot saved to: {filepath}")

main()