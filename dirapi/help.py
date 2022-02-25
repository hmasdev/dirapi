from enum import Enum
from logging import getLogger, Logger
import inspect
import re
from typing import Collection


class _NameAttr(Enum):
    QUALNAME: str = "__qualname__"
    NAME: str = "__name__"


def help_tree(
    obj: object,
    use_qualname: bool = True,
    hierarchical_symbol: str = "-->",
    skip_attr_patterns: Collection[str] = (r"^__.+__$", ),
    logger: Logger = getLogger(__name__),
) -> str:
    """Show the object structure with printing its attributes recursively.

    Args:
        obj (object): target object whose structure you want to know.
        use_qualname (bool, optional):
            Flag to use __qualname__ as the name attribute of object. Defaults to True.
            If use_qualname is False, __name__ will be used as the name attribute of object.
        hierarchical_symbol (str, optional):
            Symbol to represent the attributes hierarchy. Defaults to "-->".
            This argument will be used only when use_qualname is False.
        skip_attr_patterns (Collection[str], optional):
            Collection of regular expression patterns of attributes which will be skipped in recursion. 
            Defaults to (r"^__.+__$", ).
        logger (Logger, optional): Logger. Defaults to getLogger(__name__).

    Returns:
        str: Attributes structure of obj

    Example:
        >>> class Outer:
                class Inner1:
                    def f(self): pass
                    def g(self): pass
                class Inner2:
                    pass
                class Inner3:
                    class InnerInner1:
                        def h(self): pass
        >>> print(help_obj(Outer))
        Outer
        Outer.Inner1
        Outer.Inner1.f
        Outer.Inner1.g
        Outer.Inner2
        Outer.Inner3
        Outer.Inner3.InnerInner1
        Outer.Inner3.InnerInner1.h
        >>> print(help_obj(Outer, False))
        Outer
        -->Inner1
        -->-->f
        -->-->g
        -->Inner2
        -->Inner3
        -->-->InnerInner1
        -->-->-->h
    """  # noqa

    if use_qualname:
        return _help(
            obj,
            name_attr=_NameAttr.QUALNAME,
            hierarchial_symbol="",
            num_of_hierarchial_symbol=0,
            alternative_name=f"Not Resolved. Check if object has {_NameAttr.QUALNAME.value}.",  # noqa
            skip_attr_patterns=skip_attr_patterns,
            logger=logger,
        )
    else:
        return _help(
            obj,
            name_attr=_NameAttr.NAME,
            hierarchial_symbol=hierarchical_symbol,
            num_of_hierarchial_symbol=0,
            alternative_name=f"Not Resolved. Check if object has {_NameAttr.NAME.value}.",  # noqa
            skip_attr_patterns=skip_attr_patterns,
            logger=logger,
        )


def _help(
    obj: object,
    name_attr: _NameAttr,
    hierarchial_symbol: str,
    num_of_hierarchial_symbol: int,
    alternative_name: str,
    skip_attr_patterns: Collection[str],
    logger: Logger = getLogger(__name__),
) -> str:
    """Implementation of help

    Args:
        obj (object): target object whose structure you want to know.
        name_attr (_NameAttr): attirbute name of the name of the object.
        hierarchial_symbol (str): symbol to represent the attributes hierarchy.
        num_of_hierarchial_symbol (int): number of hierarchial_symbols which will be used in this call.
        alternative_name (str): alternative name when the name of the object is failed to be extracted with name_attr.
        skip_attr_patterns (Collection[str]): collection of regular expression patterns of attributes which will be skipped in recursion.
        logger (Logger, optional): logger. Defaults to getLogger(__name__).

    Returns:
        str: Attributes structure of obj
    """  # noqa

    # preparation
    header: str = hierarchial_symbol * num_of_hierarchial_symbol

    # init
    try:
        obj_name: str = getattr(obj, name_attr.value)
        s: str = f"{header}{obj_name}\n"
    except AttributeError:
        return f"{header}{alternative_name}\n"

    # call _help recursively
    for attr_name, attr in inspect.getmembers(obj):

        if attr is obj:
            # to avoid infinite loop
            continue

        if any([
            re.match(pttrn, attr_name)
            for pttrn in skip_attr_patterns
        ]):
            # skip patterns
            continue

        # update
        s = s + _help(
            attr,
            name_attr,
            hierarchial_symbol,
            num_of_hierarchial_symbol + 1,
            attr_name if name_attr != _NameAttr.QUALNAME else f"{obj_name}.{attr_name}",  # noqa
            skip_attr_patterns,
            logger,
        )

    return s
