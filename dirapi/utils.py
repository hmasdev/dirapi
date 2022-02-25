import re


def snake2camel(snake: str) -> str:
    """Snake case to upper camel case

    Args:
        snake (str): string in snake case

    Returns:
        str: string in upper camel case

    Example:
        >>> snake2camel("abc")
        'Abc'
        >>> snake2camel("abc_def")
        'AbcDef'
        >>> snake2camel("a_b_c_def_ghi")
        'ABCDefGhi'
        >>> snake2camel("Abc")
        'Abc'
        >>> snake2camel("__abc")
        '__Abc'
        >>> snake2camel("abc__def__")
        'AbcDef__'

    NOTE:
        1. Capitalize the first letter;
        2. Capitalize letters following underscores.
        3. Delete all underscores except for leading and trailing underscores.
    """
    # _x -> _X
    camel: str = re.sub(r"((_[^_])|(^[^_]))", lambda m: m.group().upper(), snake)  # noqa
    # __Aa__Bb__Cc__ -> __AaBbCc__
    camel = re.sub(r"(?<=[^^_])_+(?=[^_$])", lambda m: m.group().replace("_", ""), camel)  # noqa
    return camel
