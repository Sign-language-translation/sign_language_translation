# export_for_cpu.py

import tensorflow as tf

# 1. Load your trained native-Keras .keras file without compiling:
model = tf.keras.models.load_model(
    "/Users/raananpevzner/try/sign_language_translation/models/local_models/3d_gcn_rnn_on_6_vpw.keras",
    compile=False
)

# 2. Export only the inference graph as a TF SavedModel:
model.save("models/local_models/for_cpu_inference.keras")

print("Exported CPU-only SavedModel to models/local_models/for_cpu_inference")