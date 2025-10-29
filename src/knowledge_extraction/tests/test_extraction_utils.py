from src.knowledge_extraction.utils import read_student_dataset_from_csv

def test_read_student_dataset_as_csv():
    file_path = "output/student_data_test.csv"
    dataset = read_student_dataset_from_csv(file_path)
    assert not dataset.empty
    assert "query" in dataset.columns
    assert "reasoning" in dataset.columns
    assert "tool_calls" in dataset.columns
    assert "model_name" in dataset.columns