from functools import partial, wraps
import itertools
from logging import Logger, getLogger
from mypy_extensions import VarArg, KwArg
import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from .utils import snake2camel


TO_UNDERSCORE_PATTERNS: str = r"(\.|-|\+|\|)"
DELETE_PATTERNS: str = r"(\(|\)|\{|\}|\[|\]|\\|\?|\*|\$|\^)"

_logger: Logger = getLogger(__name__)


class Directory(type):
    """Metaclass for a directory
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type],
        namespace: Dict[str, Any],
        root: str,
        func_map: Optional[Dict[str, Callable[[str, VarArg(), KwArg()], Any]]] = None,  # noqa
        ext_2_func_map: Optional[Dict[str, Dict[str, Callable[[str, VarArg(), KwArg()], Any]]]] = None,  # noqa
    ):
        f"""Metaclass for a directory

        Args:
            mcs (_type_): 
            name (str):
                The class name which becomes the __name__ attribute.
            bases (Tuple[type]):
                Tuple containing the base classes which becomes the __bases__ attribute.
            namespace (Dict[str, Any]):
                Dictionary containing attributes and method definitions for the class body.
            root (Optional[str], optional):
                The path to root directory. Defaults to None.
            func_map (Optional[Dict[str, Callable[[str, VarArg, optional): 
                (attribute name, method)-dictionary which File metaclasses have. Defaults to None.
                The path associated with an instance of File will be given to the first argument of the methods.
            ext_2_func_map (Optional[Dict[str, Dict[str, Callable[[str, VarArg, optional):
                (file extension, Dictionary of attribute names and methods)-dictionary. Defaults to None.

        NOTE:
            func_map and ext_2_func_map are given priority in this order.
            For example, when you give both func_map and ext_2_func_map to Dictionary, 
            ext_2_func_map will not be used but func_map will be used.

        """  # noqa
        _logger.debug(f"Dictionary.__new__ called: name={name}, bases={bases}, namespace={namespace}, root={root}")  # noqa

        # preparation
        # copy namespace because all classes in this structure including nested classses have this namespace  # noqa
        # NOTE: the value for key="__qualname__" will be updated below.
        namespace = dict(**namespace)
        # namespace for this class
        namespace_update = dict(**namespace)

        # get files and dirs under the root directory.
        dirs: List[str] = [
            name for name in os.listdir(root)
            if os.path.isdir(os.path.join(root, name))
        ]
        files: List[str] = [
            name for name in os.listdir(root)
            if os.path.isfile(os.path.join(root, name))
        ]

        # create files and directories iterator
        iterator = itertools.chain(
            zip(
                files,
                [File] * len(files),
                [(func_map, ext_2_func_map)] * len(files),
            ),
            zip(
                dirs,
                [Directory] * len(dirs),
                [(None, None)] * len(dirs)
            ),
        )

        # add nested class for files to namespace_update
        for name_, typ, (func_map_, ext_2_func_map_) in iterator:

            # preparation
            camel_name: str = snake2camel(os.path.splitext(name_)[0])
            camel_name = re.sub(TO_UNDERSCORE_PATTERNS, "_", camel_name)
            camel_name = re.sub(DELETE_PATTERNS, "", camel_name)

            # create a namespace if the nested class
            namespace_ = _create_func_map(
                root,
                name_,
                func_map_,
                ext_2_func_map_,
            )
            # update the namespace of the nested class
            # NOTE: .update will be namespace | kwargs when python >= 3.9
            namespace_.update(**namespace)
            namespace_["__qualname__"] = f"{namespace.get('__qualname__', name)}.{camel_name}"  # type: ignore # noqa

            # warning
            if camel_name in namespace_update:
                _logger.warning(f"There are duplicated names in {root} when names are transformed to snake case.")  # noqa

            # update the namespace of this class
            namespace_update[camel_name] = typ(
                name,
                bases,
                namespace_,
                root=os.path.join(root, name_),
                func_map=func_map,
                ext_2_func_map=ext_2_func_map,
            )

        _logger.debug(f"Dictionary.__new__ exit: name={name}, bases={bases}, namespace={namespace}")  # noqa
        return super().__new__(mcs, name, bases, namespace_update)

    def __init__(cls, name, bases, namespace, *args, **kwargs):
        _logger.debug(f"Dictionary.__init__ called: name={name}, bases={bases}, namespace={namespace}")  # noqa
        super().__init__(name, bases, namespace)


class File(type):
    """Metaclass for a file
    """

    def __new__(mcs, name, bases, namespace, *args, **kwargs):
        _logger.debug(f"File.__new__ called: name={name}, bases={bases}, namespace={namespace}")  # noqa
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, *args, **kwargs):
        _logger.debug(f"File.__init__ called: name={name}, bases={bases}, namespace={namespace}")  # noqa
        super().__init__(name, bases, namespace)


def _create_func_map(
    dir: str,
    name: str,
    func_map: Optional[Dict[str, Callable[[str, VarArg(), KwArg()], Any]]] = None,  # noqa
    ext_2_func_map: Optional[Dict[str, Dict[str, Callable[[str, VarArg(), KwArg()], Any]]]] = None,  # noqa
) -> Dict[str, Callable[[str, VarArg(), KwArg()], Any]]:
    f"""Create new func_map from func_map or ext_2_func_map to handle them in the same format.

    Args:
        dir (str): directory path 
        name (str): file name or directory name in dir
        func_map (Optional[Dict[str, Callable[[str, VarArg, optional): 
            (attribute name, method)-dictionary which File metaclasses have. Defaults to None.
            The path corresponding a File metaclass will be given to the first argument of the methods.
        ext_2_func_map (Optional[Dict[str, Dict[str, Callable[[str, VarArg, optional):
            (File extension, Dictionary of attribute names and methods)-dictionary. Defaults to None.

    Returns:
        Dict[str, Callable[[str, VarArg(), KwArg()], Any]]: (attribute name, method)-dictionary.

    NOTE:
        func_map and ext_2_func_map are given priority in this order.
        For example, when you give both func_map and ext_2_func_map to Dictionary, 
        ext_2_func_map will not be used but func_map will be used.

    """  # noqa

    # preparation
    path = os.path.join(dir, name)
    splitted_name, splitted_ext = os.path.splitext(name)

    # extract func_map
    if func_map is not None:
        func_map = dict(**func_map)
    elif ext_2_func_map is not None:
        func_map = dict(**ext_2_func_map.get(splitted_ext, {}))
    else:
        func_map = {}

    # wrap func with path
    for k, v in func_map.items():
        func_map[k] = wraps(v)(partial(v, path))
        del func_map[k].__dict__["__qualname__"]  # TODO: Is there better way?

    return func_map
