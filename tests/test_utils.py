import pytest
from dirapi.utils import snake2camel


@pytest.mark.parametrize(
    "snake,camel",
    [
        ("abc", 'Abc'),
        ("abc_def", 'AbcDef'),
        ("a_b_c_def_ghi", 'ABCDefGhi'),
        ("Abc", 'Abc'),
        ("_abc", '_Abc'),
        ("abc_def_", 'AbcDef_'),
        ("__abc", '__Abc'),
        ("abc__def__", 'AbcDef__'),
        ("___abc", '___Abc'),
        ("abc___def___", 'AbcDef___'),
    ]
)
def test_snake2camel(snake: str, camel: str):
    assert snake2camel(snake) == camel
