import yaml
import tempfile
from query.generation.utils import load_config, load_generator_config, load_templater_config

def test_load_full_config():
    sample_config = {
        "dataset": {"name": "test_dataset"},
        "templater": {"templates_per_tool": 5, "temperature": 0.7},
        "generator": {"model": "test-model", "temperature": 0.9}
    }
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
        yaml.dump(sample_config, tmp)
        tmp_path = tmp.name
    
    config = load_config(tmp_path)
    assert config['dataset']['name'] == "test_dataset"
    assert config['templater']['templates_per_tool'] == 5
    assert config['templater']['temperature'] == 0.7
    assert config['generator']['model'] == "test-model"
    assert config['generator']['temperature'] == 0.9


def test_load_templater_config():
    sample_config = {
        "dataset": {"name": "test_dataset"},
        "templater": {"templates_per_tool": 5, "temperature": 0.7},
        "generator": {"model": "test-model", "temperature": 0.9}
    }
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
        yaml.dump(sample_config, tmp)
        tmp_path = tmp.name
    
    templater_config = load_templater_config(tmp_path, "templater")
    assert templater_config['templates_per_tool'] == 5
    assert templater_config['temperature'] == 0.7


def test_load_generator_config():
    sample_config = {
        "dataset": {"name": "test_dataset"},
        "templater": {"templates_per_tool": 5, "temperature": 0.7},
        "generator": {"model": "test-model", "temperature": 0.9}
    }
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
        yaml.dump(sample_config, tmp)
        tmp_path = tmp.name
    
    generator_config = load_generator_config(tmp_path, "generator")
    assert generator_config['model'] == "another-model"
    assert generator_config['temperature'] == 0.8