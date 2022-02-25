import json
import os
import pytest
import shutil
from typing import Any, Callable, Dict, Iterator, Union

from dirapi.meta import (
    Directory,
    File,
)
from dirapi.utils import snake2camel


DictStructure = Dict[str, Union[str, "DictStructure"]]  # type: ignore

# directory/file structure
# Directory -> dict, File -> str
# You have to modify tests if you change this structure
structure: DictStructure = {
    "_sample_outer": {
        "_sample_inner(1)": {
            "_test1.txt": "test1 content",
            "_test2.txt": "test2 content",
        },
        "_sample_inner[2]": {
            "_sample_inner{2}_1": {
                "_test.3.json": "[1,2,3]",
                "_test-4.json": "[1,2,3]",
            }
        },
        "_sample_inner3": {}
    }
}


def create_directories(dic: DictStructure, root: str):

    # create root
    os.makedirs(root, exist_ok=True)

    # create directories recursively
    for k, v in dic.items():
        path: str = os.path.join(root, k)

        if isinstance(v, str):
            # file case
            with open(path, "w") as f:
                f.write(v)
        elif isinstance(v, Dict):
            # directory case
            create_directories(v, path)
        else:
            continue


@pytest.fixture(scope="module")
def sample_directory(
    root: str = "./_test_structure",
) -> Iterator[str]:
    """Create sample directory structure

    Args:
        dir (str, optional): workspace. Defaults to "./_test_structure".

    Yield:
        str: path

    Warning:
        root directory will be deleted at the end of this function
    """

    # assert
    assert root != "./"
    assert os.path.abspath(root) != os.path.abspath("./")

    # create
    create_directories(structure, root)

    yield root

    if os.path.exists(root):
        shutil.rmtree(root)


def test_directory_file_for_func_map(sample_directory: str):

    # preparation
    root: str = sample_directory
    func_map: Dict[str, Callable[[str], Any]] = {
        "get_path": lambda path: path,
        "read": lambda path: open(path).read(),
    }

    # execute
    Api: Directory = Directory(
        snake2camel(os.path.basename(root)),
        (),
        {},
        root,
        func_map,
        None,
    )

    # assert
    assert isinstance(Api, Directory)  # type: ignore
    assert isinstance(Api._SampleOuter, Directory)  # type: ignore
    assert isinstance(Api._SampleOuter._SampleInner1, Directory)  # type: ignore# noqa
    assert isinstance(Api._SampleOuter._SampleInner1._Test1, File)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner1._Test2, File)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner2, Directory)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21, Directory)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, File)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, File)  # type: ignore # noqa
    assert isinstance(Api._SampleOuter._SampleInner3, Directory)  # type: ignore # noqa

    actual = getattr(Api._SampleOuter._SampleInner1._Test1, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner(1)", "_test1.txt")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test2, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner(1)", "_test2.txt")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner[2]", "_sample_inner{2}_1", "_test.3.json")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner[2]", "_sample_inner{2}_1", "_test-4.json")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test1, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner1._Test1, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test2, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner1._Test2, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected


def test_directory_file_for_ext_2_func_map(sample_directory: str):

    # preparation
    root: str = sample_directory
    ext_2_func_map: Dict[str, Dict[str, Callable[[str, ], Any]]] = {
        ".txt": {
            "get_path": lambda path: path,
            "read": lambda path: open(path).read(),
        },
        ".json": {
            "get_path": lambda path: path,
            "read": lambda path: json.load(open(path)),
        }
    }

    # execute
    Api: Directory = Directory(
        snake2camel(os.path.basename(root)),
        (),
        {},
        root,
        None,
        ext_2_func_map,
    )

    # assert
    assert isinstance(Api, Directory)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter, Directory)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner1, Directory)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner1._Test1, File)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner1._Test2, File)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner2, Directory)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21, Directory)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, File)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, File)  # type: ignore  # noqa
    assert isinstance(Api._SampleOuter._SampleInner3, Directory)  # type: ignore  # noqa

    actual = getattr(Api._SampleOuter._SampleInner1._Test1, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner(1)", "_test1.txt")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test2, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner(1)", "_test2.txt")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner[2]", "_sample_inner{2}_1", "_test.3.json")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "get_path")()  # type: ignore  # noqa
    expected = os.path.join(root, "_sample_outer", "_sample_inner[2]", "_sample_inner{2}_1", "_test-4.json")  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test1, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner1._Test1, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner1._Test2, "read")()  # type: ignore  # noqa
    expected = open(getattr(Api._SampleOuter._SampleInner1._Test2, "get_path")()).read()  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "read")()  # type: ignore  # noqa
    expected = json.load(open(getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_3, "get_path")()))  # type: ignore  # noqa
    assert actual == expected

    actual = getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "read")()  # type: ignore  # noqa
    expected = json.load(open(getattr(Api._SampleOuter._SampleInner2._SampleInner21._Test_4, "get_path")()))  # type: ignore  # noqa
    assert actual == expected
