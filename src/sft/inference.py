from unsloth import FastLanguageModel
import torch


model, tokenizer = FastLanguageModel.from_pretrained(
    "full-demo-student-model-4e",
    max_seq_length=1024,
)

FastLanguageModel.for_inference(model)

prompt = """### Input:
Combine the two words hello and world into a single string.
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.inference_mode():
    outputs = model.generate(**inputs, max_new_tokens=100)

print("🧠 Generated Output:")
print(tokenizer.decode(outputs[0], skip_special_tokens=True))