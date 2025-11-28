import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
from datasets import Dataset
import yaml
import json
import os

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_dataset_from_axiom_hive(data_dir: str) -> Dataset:
    """
    Create a dataset from Axiom Hive JSONs.
    Assumes JSONs contain 'directive' and 'correct_response' fields.
    """
    data = []
    for file in os.listdir(data_dir):
        if file.endswith('.json'):
            with open(os.path.join(data_dir, file), 'r') as f:
                axiom_data = json.load(f)
                # Format as instruction-response pairs
                data.append({
                    'instruction': axiom_data.get('directive', ''),
                    'response': axiom_data.get('correct_response', '')
                })

    return Dataset.from_list(data)

def format_instruction(example):
    return {
        'text': f"Directive: {example['instruction']}\nResponse: {example['response']}"
    }

def main():
    config = load_config('config/lex_config.yaml')

    # Load base Mamba model (using transformers wrapper for simplicity)
    model_name = config['model']['base_model']
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Add padding token if missing
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load dataset
    dataset = create_dataset_from_axiom_hive('data/')
    dataset = dataset.map(format_instruction)

    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # LoRA configuration
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["x_proj", "embeddings", "in_proj", "out_proj"],  # Mamba-specific modules
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # Training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=config['training']['epochs'],
        per_device_train_batch_size=config['training']['batch_size'],
        save_steps=10_000,
        save_total_limit=2,
        logging_dir='./logs',
        logging_steps=100,
        learning_rate=2e-4,
        weight_decay=0.01,
        fp16=True,
        dataloader_pin_memory=False,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # Train
    trainer.train()

    # Save the fine-tuned model
    model.save_pretrained('./models/lex_fine_tuned')
    tokenizer.save_pretrained('./models/lex_fine_tuned')

if __name__ == "__main__":
    main()
