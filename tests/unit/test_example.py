import pytest


class TestExampleUnit:
    
    @pytest.mark.unit
    def test_example_addition(self):
        assert 2 + 2 == 4
    
    @pytest.mark.unit
    def test_example_string_operations(self):
        text = "Hyprland Settings"
        assert text.lower() == "hyprland settings"
        assert text.upper() == "HYPRLAND SETTINGS"
        assert len(text) == 17
    
    @pytest.mark.unit
    def test_example_list_operations(self):
        items = [1, 2, 3, 4, 5]
        assert len(items) == 5
        assert sum(items) == 15
        assert max(items) == 5
        assert min(items) == 1
    
    @pytest.mark.unit
    def test_example_dictionary_operations(self):
        config = {
            "general:border_size": "2",
            "general:gaps_in": "5",
            "animations:enabled": "true"
        }
        
        assert len(config) == 3
        assert "general:border_size" in config
        assert config["general:border_size"] == "2"
        assert config.get("nonexistent", "default") == "default"
    
    @pytest.mark.unit
    @pytest.mark.parametrize("input_value,expected", [
        (0, False),
        (1, True),
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
    ])
    def test_example_boolean_conversion(self, input_value, expected):
        def to_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, int):
                return bool(value)
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return False
        
        assert to_bool(input_value) == expected


class TestExampleFixtures:
    
    @pytest.mark.unit
    def test_temp_dir_fixture_works(self, temp_dir):
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        assert test_file.exists()
        assert test_file.read_text() == "Hello, World!"
    
    @pytest.mark.unit
    def test_mock_config_dir_fixture_works(self, mock_config_dir):
        assert mock_config_dir.exists()
        assert mock_config_dir.is_dir()
        assert "hyprland-settings" in str(mock_config_dir)
    
    @pytest.mark.unit
    def test_sample_hyprctl_json_fixture_works(self, sample_hyprctl_json):
        import json
        
        assert sample_hyprctl_json.exists()
        
        with open(sample_hyprctl_json, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        for item in data:
            assert 'key' in item
            assert 'value' in item