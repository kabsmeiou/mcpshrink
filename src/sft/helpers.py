from .utils import format_data_for_sft, parse_student_dataset_from_csv, save_jsonl_file


dataset = parse_student_dataset_from_csv("output/student_data.csv")
formatted_data = format_data_for_sft(dataset)
# print(f"Loaded {len(dataset)} student dataset entries.")
# print(f"First entry: {dataset[0]}")
save_jsonl_file(formatted_data, "output/student_data_sft.jsonl")

print(f"Formatted first entry for SFT: {formatted_data[0]}")