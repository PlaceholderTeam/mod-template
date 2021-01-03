from ruamel.yaml.comments import CommentedMap, CommentedSeq

# Track how many lines have been added
lines_added = 0
# Track the previous line modified
previous_line = 0

placeholders = {
    'placeholder_key': 'placeholder_value'
}


def setPlaceholders(newPlaceholders):
    if type(newPlaceholders) != dict:
        raise TypeError('Must be dict, not ' + type(newPlaceholders))

    global placeholders
    placeholders = newPlaceholders


def executeCommand(command, commandData, filePath):
    if command == "insert":
        __insert__(commandData, filePath)
    elif command == "delete":
        __delete__(commandData, filePath)
    elif command == "erase":
        __erase__(commandData, filePath)
    elif command == "replace":
        __replace__(commandData, filePath)
    elif command == "placeholder":
        __placeholder__(commandData, filePath)
    else:
        raise RuntimeError('Unknown command ' + command)


def __checkLine__(line):
    """Check if the line input is valid

    Args:
            line (int, CommentedSeq): the line to check
    """
    global previous_line

    if type(line) == int:
        if line == previous_line:
            raise RuntimeError('Lines should not be modified twice')
        elif line < previous_line:
            raise RuntimeError('The lines in the .mtplin should be in raising order')
    elif type(line) == CommentedSeq:
        __checkLine__(int(line[0]))
        __checkLine__(int(line[1]))

        if line[0] >= line[1]:
            raise RuntimeError('The start line must not be equal or greater than the end line')


def __readContents__(filePath):
    with open(filePath, 'r') as f:
        contents = f.readlines()
        f.close()

        return contents


def __replacePlaceholder__(string, placeholder, count):
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


def __insert__(commandData, filePath):
    global lines_added
    global previous_line

    line = commandData['line']
    __checkLine__(line)

    if type(line) != int:
        raise TypeError('commands.insert.line must be int, not ' + type(line))

    text = commandData['text']

    contents = __readContents__(filePath)
    contents.insert(line + lines_added, text)
    contents = "".join(contents)

    f = open(filePath, 'w')
    f.write(contents)
    f.close()

    lines_added += len(text.split('\n')) - 1
    previous_line = line

    print(f"{filePath}: Inserted text at line {line}")


def __delete__(commandData, filePath):
    global lines_added
    global previous_line

    line = commandData['line']
    __checkLine__(line)

    contents = __readContents__(filePath)

    f = open(filePath, 'w')
    if type(line) == int:
        for i, lineStr in enumerate(contents):
            if i + 1 != line + lines_added:
                f.write(lineStr)
        f.close()

        lines_added -= 1
        previous_line = line

        print(f"{filePath}: Deleted line {line}")

    elif type(line) == CommentedSeq:
        for i, lineStr in enumerate(contents):
            if i + 1 - lines_added not in range(line[0], line[1] + 1):
                f.write(lineStr)
        f.close()

        lines_added -= line[1] + 1 - line[0]
        previous_line = line[1]

        print(f"{filePath}: Deleted lines from {line[0]} to {line[1]}")


def __erase__(commandData, filePath):
    global lines_added
    global previous_line

    line = commandData['line']
    __checkLine__(line)

    contents = __readContents__(filePath)

    f = open(filePath, 'w')
    if type(line) == int:
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
        for i, lineStr in enumerate(contents):
            if i + 1 - lines_added not in range(line[0], line[1] + 1):
                f.write(lineStr)
            else:
                f.write('\n')
        f.close()

        # Not modifying lines_added because the line isn't deleted, only the contents are
        previous_line = line[1]

        print(f"{filePath}: Erased lines from {line[0]} to {line[1]}")


def __replace__(commandData, filePath):
    global lines_added
    global previous_line

    line = commandData['line']
    __checkLine__(line)

    from_ = commandData['from']
    to = commandData['to']

    try:
        count = commandData['count']
    except KeyError:
        count = -1

    contents = __readContents__(filePath)

    f = open(filePath, 'w')
    if type(line) == int:
        for i, lineStr in enumerate(contents):
            if i + 1 != line + lines_added:
                f.write(lineStr)
            else:
                f.write(lineStr.replace(from_, to, count))
        f.close()

        previous_line = line

        print(f"{filePath}: Replaced from '{from_}' to '{to}' on line {line}")

    elif type(line) == CommentedSeq:
        for i, lineStr in enumerate(contents):
            if i + 1 - lines_added not in range(line[0], line[1] + 1):
                f.write(lineStr)
            else:
                f.write(lineStr.replace(from_, to, count))
        f.close()

        previous_line = line[1]

        print(
            f"{filePath}: Replaced from '{from_}' to '{to}' on lines from {line[0]} to {line[1]}")


def __placeholder__(commandData, filePath):
    global lines_added
    global previous_line

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

    f = open(filePath, 'w')
    if type(line) == int:
        for i, lineStr in enumerate(contents):
            if i + 1 != line + lines_added:
                f.write(lineStr)
            else:
                f.write(__replacePlaceholder__(lineStr, placeholder, count))
        f.close()

        previous_line = line

        if placeholder != "":
            print(f"{filePath}: Replaced placeholder '{placeholder}' on line {line}")
        else:
            print(f"{filePath}: Replaced placeholders on line {line}")

    elif type(line) == CommentedSeq:
        for i, lineStr in enumerate(contents):
            if i + 1 - lines_added not in range(line[0], line[1]):
                f.write(lineStr)
            else:
                f.write(__replacePlaceholder__(lineStr, placeholder, count))
        f.close()

        previous_line = line

        if placeholder != "":
            print(
                f"{filePath}: Replaced placeholder '{placeholder}' on lines from {line[0]} to {line[1]}")
        else:
            print(
                f"{filePath}: Replaced placeholders on lines from {line[0]} to {line[1]}")
