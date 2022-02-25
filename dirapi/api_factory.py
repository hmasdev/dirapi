from mypy_extensions import VarArg, KwArg
from typing import Any, Callable, Dict, Optional


from .meta import Directory


def create_api(
    root_dir: str,
    func_map: Optional[Dict[str, Callable[[str, VarArg(), KwArg()], Any]]] = None,  # noqa
    ext_2_func_map: Optional[Dict[str, Dict[str, Callable[[str, VarArg(), KwArg()], Any]]]] = None,  # noqa
):
    """Create api associated with directories' structure

    For example, if you have the following directories

        data/
            images/
                img001.png
                img002.png
            labels/
                label001.txt
                label002.txt
            output.csv

    create_api provides the following class structure:

        class Data:
            class Images:
                class Img001
                    ...
                class Img002
                    ...
            class Labels:
                class Label001
                    ...
                class Label002
                    ...
            class Output:
                ...

    where ... will become your custom methods like data loaders.

    Args:
        root_dir (str): the path to root directory.
        func_map (Optional[Dict[str, Callable[[str, VarArg, optional):
            (attribute name, method)-dictionary which the classes associated with files have. Defaults to None.
            The first argument is the path to a file in the directory structure.
        ext_2_func_map (Optional[Dict[str, Dict[str, Callable[[str, VarArg, optional):
            (File extension, Dictionary of attribute names and methods)-dictionary. Defaults to None.

    Returns:
        Directory: Api for the directory.

    NOTE:
        func_map and ext_2_func_map are given priority in this order.
        For example, when you give both func_map and ext_2_func_map to create_api,
        ext_2_func_map will not be used but func_map will be used.

    """  # noqa
    return Directory("Api", (), {}, root_dir, func_map, ext_2_func_map)
