#!/usr/bin/python3
from ruamel.yaml import YAML as YML
from ruamel.yaml.comments import CommentedSeq
from io import TextIOWrapper
import ntpath
import argparse
import os
import re
import shutil
import subprocess
import template.commands as cmds

YAML = YML()


def __replace_up_a__(match):
    string = match.group(0).upper()
    if match.group(1) == '-':
        string = string[1:]
    return string


def __replace_up_b__(match):
    string = match.group(0).upper()
    if match.group(1) == '-':
        string = ' ' + string[1:]
    return string


# Arguments
argparser = argparse.ArgumentParser(description='Generate a mod.')
argparser.add_argument('mod-id', type=str, help='The id to give to the mod.')
argparser.add_argument('-p', '--package-name', type=str,
                       nargs='?', help='Set a package name to give to the mod.')
argparser.add_argument('-c', '--class-name', type=str, nargs='?',
                       help='Set a class name for the mod initializer.')
argparser.add_argument('-n', '--name', type=str,
                       nargs='?', help='Set a name for the mod.')
argparser.add_argument('-i', '--namespace', type=str,
                       nargs='?', help='Set a namespace to give to the mod.')
argparser.add_argument('-v', '--version', type=str,
                       nargs='?', help='Set a starting version to give to the mod.')

argparser.add_argument('-CF', '--curseforge', action='store_true',
                       help='Use Curseforge/Cursegradle with the mod publication.')
argparser.add_argument('-GH', '--github-actions', action='store_true',
                       help='Use Github Actions CI with the mod repository.')
argparser.add_argument('-M', '--modrinth', action='store_true',
                       help='Use Modrinth/Minotaur with the mod publication.')
argparser.add_argument('-MX', '--mixin', action='store_true',
                       help='Use mixins on the mod.')

argparser.add_argument('-d', '--debug', action='store_true',
                       help='Use the script in debug mode. It won\'t delete itself or the template and it won\'t make any actual operation.')

arguments = vars(argparser.parse_args())


MOD_ID = arguments.get('mod-id')
PACKAGE_NAME = arguments.get('package_name')
CLASS_NAME = arguments.get('class_name')
MOD_NAME = arguments.get('name')
MOD_NAMESPACE = arguments.get('namespace')
MOD_VERSION = arguments.get('version')

# Set defaults
if PACKAGE_NAME == None:
    PACKAGE_NAME = MOD_ID.replace('-', '')
if CLASS_NAME == None:
    CLASS_NAME = re.sub('(-|^)([a-z])', __replace_up_a__, MOD_ID)
if MOD_NAME == None:
    MOD_NAME = re.sub('(-|^)([a-z])', __replace_up_b__, MOD_ID)
if MOD_NAMESPACE == None:
    MOD_NAMESPACE = MOD_ID.replace('-', '_')
if MOD_VERSION == None:
    MOD_VERSION = '1.0.0'


REPO_NAME = os.path.basename(os.getcwd())

USE_CURSEFORGE = arguments.get('curseforge')
USE_GH_ACTIONS = arguments.get('github_actions')
USE_MODRINTH = arguments.get('modrinth')
USE_MIXIN = arguments.get('mixin')

DEBUG_MODE = arguments.get('debug', False)

# Print info
print(f"New mod ID = '{MOD_ID}'")
print(f"New package name = '{PACKAGE_NAME}'")
print(f"New class name = '{CLASS_NAME}'")
print(f"New mod name = '{MOD_NAME}'")
print(f"New mod namespace = '{MOD_NAMESPACE}'")
print(f"New mod start version = '{MOD_VERSION}'")
print(f"Current directory/repository name = '{REPO_NAME}'")
print('\n')

usages = []

if USE_CURSEFORGE:
    usages.append('Curseforge')
if USE_GH_ACTIONS:
    usages.append('Github Actions')
if USE_MODRINTH:
    usages.append('Modrinth')
if USE_MIXIN:
    usages.append('Mixin')

if len(usages) > 0:
    if len(usages) == 1:
        print(f"Using {usages[0]}\n")
    else:
        string = ", ".join(usages[:-1])
        string = string + " & " + usages[-1]
        print(f"Using {string}\n")

if DEBUG_MODE:
    print("Running on debug mode!\n")
    cmds.setDebugMode(DEBUG_MODE)

response = input("Are you sure? [y/N] ")

if not (response.startswith('y') or response.lower() == 'yes'):
    print("Aborting.")
    exit(1)


def updatePlaceholders():
    global MOD_ID
    global PACKAGE_NAME
    global CLASS_NAME
    global MOD_NAME
    global MOD_NAMESPACE
    global REPO_NAME
    global MOD_VERSION
    placeholders = {
        'template-mod-id': MOD_ID,
        'templatemodpkg': PACKAGE_NAME,
        'TemplateModClass': CLASS_NAME,
        'Template_Mod_Name': MOD_NAME,
        'template_mod': MOD_NAMESPACE,
        'template-mod-dir': REPO_NAME,
        'template-mod-ver': MOD_VERSION,
    }

    cmds.setPlaceholders(placeholders)


def runCondition(condition: str):
    conditions = {
        'cf': USE_CURSEFORGE,
        'gh': USE_GH_ACTIONS,
        'm': USE_MODRINTH,
        'mx': USE_MIXIN,
        'linux': os.name != 'nt'
    }

    try:
        return conditions[condition]
    except KeyError:
        if '||' in condition or '&&' in condition or '!' in condition:
            new_condition = condition.replace('||', 'or')
            new_condition = new_condition.replace('&&', 'and')
            new_condition = new_condition.replace('!', 'not')

            hasKey = False
            for key in list(conditions.keys()):
                if key in new_condition:
                    hasKey = True
                    new_condition = new_condition.replace(
                        key, str(conditions[key]))

            if hasKey:
                return eval(new_condition)
            else:
                return False
        else:
            raise KeyError(f"{condition} is not a valid condition")
    return False


def runCommand(commandYaml: CommentedSeq, filePath: str):
    command = list(commandYaml.keys())[0]
    commandData = commandYaml[command]

    try:
        condition = commandData['if']
    except KeyError:
        condition = ""

    if condition != "":
        try:
            else_command = commandData['else']
        except KeyError:
            else_command = ""

        if runCondition(condition):
            cmds.executeCommand(command, commandData, filePath)
        elif else_command != "":
            cmds.executeCommand(else_command, commandData, filePath)
    else:
        cmds.executeCommand(command, commandData, filePath)


def runTpl(templateFile: TextIOWrapper):
    global DEBUG_MODE
    print('Loading and running template', ntpath.basename(templateFile.name))

    cmds.resetVars()

    data = YAML.load(templateFile)
    templateFile.close()

    filePath = data['file']

    if '¿' in filePath:
        filePath = cmds.__replaceInlinePlaceholder__(filePath)

    # If
    try:
        tpl_condition = data['if']
        if not runCondition(tpl_condition):
            print('Aborting template usage: if condition not met')
            print('--')
            return

    except KeyError:
        pass

    # Action
    try:
        action = data['action']

        if action == "create":
            path = filePath.split('/')

            # Create folder if it doesn't exist
            if len(path) > 1:
                fileDir = '/'.join(path[:-1])

                if not os.path.exists(fileDir):
                    if not DEBUG_MODE:
                        os.makedirs(fileDir)
                    print(f"Created directory => {fileDir}")

            # Create file
            print(f"Created file => {filePath}")
            if not DEBUG_MODE:
                f = open(filePath, 'w')
                f.close()
            else:
                # Direct to script to avoid FileNotFoundError because the file wasn't created
                filePath = 'main.py'

        elif action == "duplicate":
            try:
                fromFilePath = data['from']
            except KeyError:
                # Save original file path
                fromFilePath = filePath

                # Add "copy" suffix to file name
                filename, file_extension = os.path.splitext(filePath)
                filePath = filename + "-copy" + file_extension

            path = filePath.split('/')

            # Create folder if it doesn't exist
            if len(path) > 1:
                fileDir = '/'.join(path[:-1])

                if not os.path.exists(fileDir):
                    if not DEBUG_MODE:
                        os.makedirs(fileDir)
                    print(f"Created directory => {fileDir}")

            print(f"Copied file from '{fromFilePath}' to '{filePath}'")
            if not DEBUG_MODE:
                shutil.copyfile(fromFilePath, filePath)
            else:
                # Direct to source file to avoid FileNotFoundError because the file wasn't copied/created
                filePath = fromFilePath

        elif action == "move":
            sourceFilePath = data['from']

            path = filePath.split('/')

            # Create folder if it doesn't exist
            if len(path) > 1:
                fileDir = '/'.join(path[:-1])

                if not os.path.exists(fileDir):
                    if not DEBUG_MODE:
                        os.makedirs(fileDir)
                    print(f"Created directory => {fileDir}")

            print(f"{sourceFilePath} => {filePath}")
            if not DEBUG_MODE:
                os.rename(sourceFilePath, filePath)
            else:
                # Direct to source file to avoid FileNotFoundError because the file wasn't moved/created
                filePath = sourceFilePath

    except KeyError:
        pass

    commands = data['commands']

    for command in commands:
        runCommand(command, filePath)

    try:
        shell_commands = data['run']

        for command in shell_commands:
            print(f"'{command}':")
            if not DEBUG_MODE:
                subprocess.run(command.split())
            print('-- Finished command --')
    except KeyError:
        pass

    print('--')


updatePlaceholders()

templateDir = os.fsencode('template/')

for file in os.listdir(templateDir):
    filename = os.fsdecode(file)
    if filename.endswith('.mtplin'):
        runTpl(open('template/' + filename, 'r'))

if not DEBUG_MODE:
    # Auto destroy the template
    shutil.rmtree('template/')

    # Auto destroy the python script
    os.remove('main.py')
