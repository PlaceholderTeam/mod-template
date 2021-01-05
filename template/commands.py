from ruamel.yaml.comments import CommentedMap, CommentedSeq
from typing import Any

# Track how many lines have been added
lines_added = 0
# Track the previous line modified
previous_line = 0

placeholders = {
    'placeholder_key': 'placeholder_value'
}

debug_mode = False


def setPlaceholders(newPlaceholders: dict):
    if type(newPlaceholders) != dict:
        raise TypeError('Must be dict, not ' + type(newPlaceholders))

    global placeholders
    placeholders = newPlaceholders


def setDebugMode(newDebugMode: bool):
    if type(newDebugMode) != bool:
        raise TypeError('Must be bool, not ' + type(newDebugMode))

    global debug_mode
    debug_mode = newDebugMode


def resetVars():
    global lines_added
    lines_added = 0
    global previous_line
    previous_line = 0


def executeCommand(command: str, commandData: CommentedMap, filePath: str):
    commands = {
        'insert': __insert__,
        'delete': __delete__,
        'erase': __erase__,
        'replace': __replace__,
        'placeholder': __placeholder__,
        'do_nothing': __doNothing__,
    }

    try:
        commands[command](commandData, filePath)
    except KeyError:
        raise RuntimeError('Unknown command ' + command)


def __checkLine__(line: Any):
    """Check if the line input is valid

    Args:
            line (int, CommentedSeq): the line to check
    """
    global previous_line

    if type(line) == int:
        if line == previous_line:
            raise RuntimeError('Lines should not be modified twice')
        elif line < previous_line:
            raise RuntimeError(
                'The lines in the .mtplin should be in raising order')
    elif type(line) == CommentedSeq:
        __checkLine__(int(line[0]))
        __checkLine__(int(line[1]))

        if line[0] >= line[1]:
            raise RuntimeError(
                'The start line must not be equal or greater than the end line')


def __readContents__(filePath: str):
    with open(filePath, 'r') as f:
        contents = f.readlines()
        f.close()

        return contents


def __replacePlaceholder__(string: str, placeholder: str, count: int):
    global placeholders

    if placeholder != "":
        try:
            replacement = placeholders[placeholder]
        except KeyError:
            raise RuntimeError('Unknown placeholder ' + placeholder)

        if placeholder in string:
            string = string.replace(placeholder, replacement, count)
    else:
        for placeholder in list(placeholders.keys()):
            if placeholder in string:
                string = string.replace(
                    placeholder, placeholders[placeholder], count)

    return string


def __replaceInlinePlaceholder__(string: str):
    global placeholders

    for placeholder in list(placeholders.keys()):
        if f"¿{placeholder}¿" in string:
            string = string.replace(
                f"¿{placeholder}¿", placeholders[placeholder])

    return string


def __insert__(commandData: CommentedMap, filePath: str):
    global lines_added
    global previous_line
    global debug_mode

    line = commandData['line']
    __checkLine__(line)

    if type(line) != int:
        raise TypeError('commands.insert.line must be int, not ' + type(line))

    text = commandData['text']

    if '¿' in text:
        text = __replaceInlinePlaceholder__(text)

    contents = __readContents__(filePath)
    contents.insert(line + lines_added, text)
    contents = "".join(contents)

    if not debug_mode:
        f = open(filePath, 'w')
        f.write(contents)
        f.close()

    lines_added += len(text.split('\n')) - 1
    previous_line = line

    print(f"{filePath}: Inserted text at line {line}")


def __delete__(commandData: CommentedMap, filePath: str):
    global lines_added
    global previous_line
    global debug_mode

    line = commandData['line']
    __checkLine__(line)

    contents = __readContents__(filePath)

    if not debug_mode:
        f = open(filePath, 'w')
    if type(line) == int:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 != line + lines_added:
                    f.write(lineStr)
            f.close()

        lines_added -= 1
        previous_line = line

        print(f"{filePath}: Deleted line {line}")

    elif type(line) == CommentedSeq:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 - lines_added not in range(line[0], line[1] + 1):
                    f.write(lineStr)
            f.close()

        lines_added -= line[1] + 1 - line[0]
        previous_line = line[1]

        print(f"{filePath}: Deleted lines from {line[0]} to {line[1]}")


def __erase__(commandData: CommentedMap, filePath: str):
    global lines_added
    global previous_line
    global debug_mode

    line = commandData['line']
    __checkLine__(line)

    contents = __readContents__(filePath)

    if not debug_mode:
        f = open(filePath, 'w')
    if type(line) == int:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 != line + lines_added:
                    f.write(lineStr)
                else:
                    f.write('\n')
            f.close()

        # Not modifying lines_added because the line isn't deleted, only the contents are
        previous_line = line

        print(f"{filePath}: Erased line {line}")

    elif type(line) == CommentedSeq:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 - lines_added not in range(line[0], line[1] + 1):
                    f.write(lineStr)
                else:
                    f.write('\n')
            f.close()

        # Not modifying lines_added because the line isn't deleted, only the contents are
        previous_line = line[1]

        print(f"{filePath}: Erased lines from {line[0]} to {line[1]}")


def __replace__(commandData: CommentedMap, filePath: str):
    global lines_added
    global previous_line
    global debug_mode

    line = commandData['line']
    __checkLine__(line)

    from_ = commandData['from']
    to = commandData['to']

    if '¿' in to:
        to = __replaceInlinePlaceholder__(to)

    try:
        count = commandData['count']
    except KeyError:
        count = -1

    contents = __readContents__(filePath)

    if not debug_mode:
        f = open(filePath, 'w')
    if type(line) == int:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 != line + lines_added:
                    f.write(lineStr)
                else:
                    f.write(lineStr.replace(from_, to, count))
            f.close()

        previous_line = line

        print(f"{filePath}: Replaced from '{from_}' to '{to}' on line {line}")

    elif type(line) == CommentedSeq:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 - lines_added not in range(line[0], line[1] + 1):
                    f.write(lineStr)
                else:
                    f.write(lineStr.replace(from_, to, count))
            f.close()

        previous_line = line[1]

        print(
            f"{filePath}: Replaced from '{from_}' to '{to}' on lines from {line[0]} to {line[1]}")


def __placeholder__(commandData: CommentedMap, filePath: str):
    global lines_added
    global previous_line
    global debug_mode

    line = commandData['line']
    __checkLine__(line)

    try:
        placeholder = commandData['placeholder']
    except KeyError:
        placeholder = ""

    try:
        count = commandData['count']
    except KeyError:
        count = -1

    contents = __readContents__(filePath)

    if not debug_mode:
        f = open(filePath, 'w')
    if type(line) == int:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 != line + lines_added:
                    f.write(lineStr)
                else:
                    f.write(__replacePlaceholder__(
                        lineStr, placeholder, count))
            f.close()

        previous_line = line

        if placeholder != "":
            print(f"{filePath}: Replaced placeholder '{placeholder}' on line {line}")
        else:
            print(f"{filePath}: Replaced placeholders on line {line}")

    elif type(line) == CommentedSeq:
        if not debug_mode:
            for i, lineStr in enumerate(contents):
                if i + 1 - lines_added not in range(line[0], line[1] + 1):
                    f.write(lineStr)
                else:
                    f.write(__replacePlaceholder__(
                        lineStr, placeholder, count))
            f.close()

        previous_line = line[1]

        if placeholder != "":
            print(
                f"{filePath}: Replaced placeholder '{placeholder}' on lines from {line[0]} to {line[1]}")
        else:
            print(
                f"{filePath}: Replaced placeholders on lines from {line[0]} to {line[1]}")


def __doNothing__(commandData: CommentedMap, filePath: str):
    pass
