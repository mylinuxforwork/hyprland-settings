import sys
import os
import json
import tempfile
from pathlib import Path
import pytest


class TestInfrastructureValidation:
    
    @pytest.mark.unit
    def test_python_version(self):
        assert sys.version_info >= (3, 10), "Python 3.10 or higher is required"
    
    @pytest.mark.unit
    def test_project_structure_exists(self):
        project_root = Path(__file__).parent.parent
        
        assert project_root.exists(), "Project root does not exist"
        assert (project_root / "src").exists(), "src directory does not exist"
        assert (project_root / "tests").exists(), "tests directory does not exist"
        assert (project_root / "tests" / "unit").exists(), "tests/unit directory does not exist"
        assert (project_root / "tests" / "integration").exists(), "tests/integration directory does not exist"
    
    @pytest.mark.unit
    def test_config_files_exist(self):
        project_root = Path(__file__).parent.parent
        
        assert (project_root / "pyproject.toml").exists(), "pyproject.toml does not exist"
        assert (project_root / "tests" / "conftest.py").exists(), "conftest.py does not exist"
    
    @pytest.mark.unit
    def test_source_modules_importable(self):
        try:
            from src.main import HyprlandSettingsApplication
            assert HyprlandSettingsApplication is not None
        except ImportError as e:
            pytest.skip(f"Cannot import main module: {e}")
        
        try:
            from src.window import HyprlandSettingsWindow
            assert HyprlandSettingsWindow is not None
        except ImportError as e:
            pytest.skip(f"Cannot import window module: {e}")
        
        try:
            from src.settings import HyprlandKeywordsSettings
            assert HyprlandKeywordsSettings is not None
        except ImportError as e:
            pytest.skip(f"Cannot import settings module: {e}")
        
        try:
            from src.library.library import Library
            assert Library is not None
        except ImportError as e:
            pytest.skip(f"Cannot import library module: {e}")
    
    @pytest.mark.unit
    def test_gtk_dependencies(self):
        try:
            import gi
            gi.require_version('Gtk', '4.0')
            gi.require_version('Adw', '1')
            from gi.repository import Gtk, Adw, Gio, GLib
            
            assert Gtk is not None
            assert Adw is not None
            assert Gio is not None
            assert GLib is not None
        except (ImportError, ValueError) as e:
            pytest.skip(f"GTK dependencies not available: {e}")
    
    @pytest.mark.unit
    def test_fixtures_available(self, temp_dir, mock_config_dir, sample_hyprctl_descriptions):
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        assert mock_config_dir.exists()
        assert mock_config_dir.is_dir()
        
        assert isinstance(sample_hyprctl_descriptions, list)
        assert len(sample_hyprctl_descriptions) > 0
    
    @pytest.mark.unit
    def test_temp_dir_fixture(self, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    @pytest.mark.unit
    def test_mock_config_fixture(self, mock_config_dir):
        test_config = mock_config_dir / "test_config.json"
        test_data = {"test": "data"}
        
        with open(test_config, 'w') as f:
            json.dump(test_data, f)
        
        assert test_config.exists()
        
        with open(test_config, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    @pytest.mark.unit
    def test_sample_hyprctl_json_fixture(self, sample_hyprctl_json):
        assert sample_hyprctl_json.exists()
        assert sample_hyprctl_json.suffix == ".json"
        
        with open(sample_hyprctl_json, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert all('key' in item and 'value' in item for item in data)
    
    @pytest.mark.unit
    def test_mock_subprocess_fixture(self, mock_subprocess):
        assert mock_subprocess is not None
        
        process = mock_subprocess()
        stdout, stderr = process.communicate()
        
        assert stdout == b"OK"
        assert stderr == b""
        assert process.returncode == 0
    
    @pytest.mark.unit
    def test_pytest_markers_defined(self):
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        content = pyproject.read_text()
        
        expected_markers = ['unit', 'integration', 'slow', 'gui', 'requires_hyprland']
        
        for marker in expected_markers:
            assert f'"{marker}:' in content, f"Marker {marker} not found in pyproject.toml"
    
    @pytest.mark.slow
    def test_slow_marker(self):
        import time
        time.sleep(0.1)
        assert True, "Slow test marker works"


class TestCoverageConfiguration:
    
    @pytest.mark.unit
    def test_coverage_configured(self):
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        assert pyproject.exists()
        
        content = pyproject.read_text()
        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content
        assert "fail_under = 80" in content
    
    @pytest.mark.unit
    def test_coverage_source_configured(self):
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        content = pyproject.read_text()
        assert 'source = ["src"]' in content
        assert "branch = true" in content


class TestPoetryConfiguration:
    
    @pytest.mark.unit  
    def test_poetry_config_exists(self):
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        assert pyproject.exists()
        
        content = pyproject.read_text()
        assert "[tool.poetry]" in content
        assert "name = " in content
        assert "version = " in content
    
    @pytest.mark.unit
    def test_test_dependencies_configured(self):
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        content = pyproject.read_text()
        assert "pytest" in content
        assert "pytest-cov" in content
        assert "pytest-mock" in content
    
    @pytest.mark.unit
    def test_poetry_scripts_configured(self):
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        content = pyproject.read_text()
        assert "[tool.poetry.scripts]" in content
        assert 'test = "pytest:main"' in content
        assert 'tests = "pytest:main"' in content