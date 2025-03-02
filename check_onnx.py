import onnx
import onnxruntime as ort
import numpy as np

model = onnx.load("pretrained_models/CosyVoice2-0.5B/flow.decoder.estimator.fp32.4090.onnx")
onnx.checker.check_model(model)
x_test = np.random.randn(5, 80, 100).astype(np.float32)  # batch_size=5, seq_len=100
mask_test = np.random.randn(5, 1, 100).astype(np.float32)
mu_test = np.random.randn(5, 80, 100).astype(np.float32)
t_test = np.random.randn(5).astype(np.float32)
spks_test = np.random.randn(5, 80).astype(np.float32)
cond_test = np.random.randn(5, 80, 100).astype(np.float32)

# Run inference
inputs = {
    "x": x_test,
    "mask": mask_test,
    "mu": mu_test,
    "t": t_test,
    "spks": spks_test,
    "cond": cond_test
}
session = ort.InferenceSession("pretrained_models/CosyVoice2-0.5B/flow.decoder.estimator.fp32.4090.onnx")

outputs = session.run(None, inputs)

print("Inference successful with batch size 5 and seq_len 100")
# Print input and output shapes
for input in session.get_inputs():
    print(f"Input: {input.name}, Shape: {input.shape}")
for output in session.get_outputs():
    print(f"Output: {output.name}, Shape: {output.shape}")
