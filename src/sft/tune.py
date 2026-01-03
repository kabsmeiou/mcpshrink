from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

from src.sft.helpers import parse_and_format_student_data

MODEL_NAME = "unsloth/gemma-2b" 
DATA_PATH = "output/student_data_sft.jsonl"
MAX_SEQ_LEN = 1024
EPOCHS = 5
LR = 2e-4
BATCH_SIZE = 2
STUDENT_MODEL_PATH = "finetuned-student-model"


def format_for_training(example):
    return {
        "text": f"### Input:\n{example['input']}\n\n### Reasoning:\n{example['output']['reason']}\n\n### Tool Calls:\n{example['output']['tool_calls']}"
    }

def tune_student_model(model_name=MODEL_NAME, data_path=DATA_PATH, student_model_path=STUDENT_MODEL_PATH):
    dataset = load_dataset("json", data_files=data_path, split="train")
    dataset = dataset.map(format_for_training)

    # load model from unsloth fastlanguagemodel
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=MAX_SEQ_LEN,
    )

    # apply PEFT LoRA for less VRAM usage
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    # create trainer with SFTTrainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LEN,  # fixed casing
        dataset_num_proc=2,
        packing=True,
        args=TrainingArguments(
            learning_rate=LR,
            lr_scheduler_type="linear",
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=4,
            num_train_epochs=EPOCHS,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            warmup_steps=10,
            output_dir="output",
            seed=42,
            save_strategy="epoch",
            report_to="none",  # disable W&B
        ),
    )

    # train and save the model
    trainer.train()
    trainer.save_model(student_model_path)
    print(f"✅ Fine-tuning complete! Model saved to {student_model_path}")

# tune_student_model(data_path="output/full_demo.jsonl", student_model_path="full-demo-student-model-4e")
