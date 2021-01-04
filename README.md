# Mod template

So, you probably are asking yourself, what is this all about? Well, it's my mod template! All my new mods, once this is done, will be generated using this template. To generate a mod, the template has a script file, which picks instructions from the [template files](#template-files) under the `template` folder.

## Template Files
To provide instructions to the script without hardcoding it, I have created files with the `.mtplin` (**M**od**T**em**PL**ate**IN**structions), located at the `template` folder. Each of these files contains a series of ["commands"](#commands) that will explain what to do.

##### Example
```yaml
# Modify the file gradle.properties
file: gradle.properties

commands:
  # Delete the first line
  - delete:
      line: 1

  # Erase lines from 7 to 13
  - erase:
      line: [7, 13]

  # Replace from "line" to "space" on line 15 only 1 time
  - replace:
      line: 15
      from: "line"
      to: "space"
      count: 1

# Run echo "test" and echo "tset" on a command line
run:
- echo "test"
- echo "tset"
```

### Reference
#### `file`
**Required** The a path to the file the template will modify.

#### `action`
A special command to execute.

##### Actions
- `create` - create the file if it doesn't exist.
- `duplicate` - create a copy of the target file. Use `from` to set the source file to duplicate, this will make the `file` the copied file.
- `move` - move a file from `from` to the target file.

#### `from`
Required if action is `move`. The source file to move/duplicate.

#### `if`
A [condition](#conditions) to be met for the template to be used.

#### `commands`
**Required** The [commands](#commands) the template will execute.

#### `commands.<command>.line`
**Required** A number to indicate which line the command will affect. An array to indicate a range of lines.

#### `commands.<command>.if`
A [condition](#conditions) to be met for the command to be executed.

#### `commands.insert.text`
**Required** The text to insert at the `line`.

#### `commands.replace.from`
**Required** The text to replace.

#### `commands.replace.to`
**Required** The text to replace with.

#### `commands.<replace|placeholder>.count`
The maximum number of times the string, or a placeholder, will be replaced. **Note:** the count is per line, it is the same for each line that it affects.

#### `commands.placeholder.placeholder`
The placeholder to replace.

#### `run`
Run commands once the template is finished.

#### `run.<command>`
**Required** The command or commands that will be run once the template is finished.

## Commands
### Command list
- `delete` - delete the line(s).
- `insert` - insert a line. the `line` part should have only one line, which is above where the text will be inserted.
- `erase` - set a line or lines to whitespace.
- `replace` - replace text **a** with text **b**. Use the `extra` part to define the text **a** and **b**.
- `placeholder` - indicate to replace the [placeholders](#placeholders) on that line or lines.
- `run` - run a command on bash/cmd

### Conditions
Most of the conditions are if the mod uses the option.
- Bintray - `b`
- Curseforge - `cf`
- Github actions - `gh`
- Modrinth - `m`
- Mixin - `mx`
- Linux - `linux` - If the system running the script is linux

## Placeholders
On the files you can set placeholders that will be replaced when using the `placeholder` command. These placeholders are:
- `template-mod-id` - the mod id
- `templatemodpkg` - the mod package
- `TemplateModClass` - the mod class
- `Template_Mod_Name` - the mod name
- `template_mod` - the mod namespace/id
- `template-mod-dir` - the mod directory/repository name
- `template-mod-ver` - the mod version.

To use placeholders inside `commands.insert.text` just put the placeholder between two `¿` (Alt + 0191).
