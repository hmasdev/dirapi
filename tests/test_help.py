import pytest
import re
from typing import Collection
from dirapi.help import _NameAttr, help_tree, _help


class Outer:
    class Inner1:
        def f(self): pass
        def g(self): pass

    class Inner2:
        pass

    class Inner3:
        class InnerInner1:
            def h(self): pass


QUALNAME_HELP = """Outer
{hierarchial_symbol}Outer.Inner1
{hierarchial_symbol}{hierarchial_symbol}Outer.Inner1.f
{hierarchial_symbol}{hierarchial_symbol}Outer.Inner1.g
{hierarchial_symbol}Outer.Inner2
{hierarchial_symbol}Outer.Inner3
{hierarchial_symbol}{hierarchial_symbol}Outer.Inner3.InnerInner1
{hierarchial_symbol}{hierarchial_symbol}{hierarchial_symbol}Outer.Inner3.InnerInner1.h
"""

NAME_HELP = """Outer
{hierarchial_symbol}Inner1
{hierarchial_symbol}{hierarchial_symbol}f
{hierarchial_symbol}{hierarchial_symbol}g
{hierarchial_symbol}Inner2
{hierarchial_symbol}Inner3
{hierarchial_symbol}{hierarchial_symbol}InnerInner1
{hierarchial_symbol}{hierarchial_symbol}{hierarchial_symbol}h
"""


@pytest.mark.parametrize(
    ",".join([
        "obj",
        "use_qualname",
        "hierarchial_symbol",
    ]),
    [
        (
            # usual pattern
            Outer,
            True,
            "",
        ),
        (
            # usual pattern
            Outer,
            False,
            "|||",
        ),
    ]
)
def test_help(
    obj: object,
    use_qualname: bool,
    hierarchial_symbol: str,
):

    # preparation
    expected: str
    if use_qualname:
        expected = QUALNAME_HELP.format(hierarchial_symbol=hierarchial_symbol)
    else:
        expected = NAME_HELP.format(hierarchial_symbol=hierarchial_symbol)

    # execute
    actual: str = help_tree(
        obj,
        use_qualname,
        hierarchial_symbol,
    )

    # assert
    assert actual == expected


@pytest.mark.parametrize(
    ",".join([
        "obj",
        "name_attr",
        "hierarchial_symbol",
    ]),
    [
        (
            # usual pattern
            Outer,
            _NameAttr.QUALNAME,
            "-->",
        ),
        (
            # usual pattern
            Outer,
            _NameAttr.NAME,
            "|||",
        ),
    ]
)
def test__help(
    obj: object,
    name_attr: _NameAttr,
    hierarchial_symbol: str,
):

    # preparation
    expected: str
    if name_attr == _NameAttr.QUALNAME:
        expected = QUALNAME_HELP.format(hierarchial_symbol=hierarchial_symbol)
    elif name_attr == _NameAttr.NAME:
        expected = NAME_HELP.format(hierarchial_symbol=hierarchial_symbol)
    else:
        raise ValueError(f"Invalid name_attr = {name_attr}")

    # execute
    actual: str = _help(
        obj,
        name_attr,
        hierarchial_symbol,
        0,
        alternative_name="ERROR",  # anything is OK.
        skip_attr_patterns=(r"^__.+__$", ),
    )

    # assert
    assert actual == expected


@pytest.mark.parametrize(
    "name_attr,alternative_name",
    [
        (_NameAttr.QUALNAME, "alternative"),
        (_NameAttr.NAME, "ERROR"),
    ]
)
def test__help_with_name_attr_not_found(
    name_attr: _NameAttr,
    alternative_name: str,
):

    # preparation
    obj: object = 1
    expected: str = alternative_name + "\n"
    # NOTE: output of _help is ended with "\n"

    # check name_attr not found
    assert not hasattr(obj, name_attr.value)

    # execute
    actual: str = _help(
        obj,
        name_attr,
        "",  # anything is ok
        0,  # any integers are valid
        alternative_name,
        (r"^__.+__$", ),
    )

    # assert
    assert actual == expected


def test__help_with_skip_attr_patterns():

    # preparation
    obj: object = Outer
    name_attr: _NameAttr = _NameAttr.QUALNAME
    hierarchial_symbol: str = ""  # anything is OK
    alternative_name: str = ""  # anything is OK
    skip_attr_patterns: Collection[str] = [r"^__.+__$", r"f"]

    # exepected
    expected: str = QUALNAME_HELP.format(hierarchial_symbol=hierarchial_symbol)
    # Delete the line including Outer.Inner1.f
    # because r"f" is in skip_attr_patterns.
    expected = re.sub(r"\n.*\.f\n", "\n", expected)

    # execute
    actual: str = _help(
        obj,
        name_attr,
        hierarchial_symbol,
        0,
        alternative_name,
        skip_attr_patterns,
    )

    # assert
    assert actual == expected
