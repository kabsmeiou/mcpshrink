from .utils import format_data_for_sft, parse_student_dataset_from_csv, save_jsonl_file

def parse_and_format_student_data(file_path: str):
    dataset = parse_student_dataset_from_csv(file_path)
    formatted_data = format_data_for_sft(dataset)
    # print(f"Loaded {len(dataset)} student dataset entries.")
    # print(f"First entry: {dataset[0]}")
    save_jsonl_file(formatted_data, "output/student_data_sft.jsonl")
    print("✅ Student dataset formatted and saved to output/student_data_sft.jsonl")