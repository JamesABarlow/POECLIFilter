import pytest


@pytest.fixture
def in_tmp_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path
