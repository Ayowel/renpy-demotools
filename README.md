# Demotools

This is a tool used to generate live demos or demo snapshots to generate gifs

## Usage

Copy a released `demotools.rpe` into the Ren'Py game's `game` folder.
Move to the game's root directory in the command line and run the `demotools` command:

```sh
# Run a specific label and stop
../../../sdk/renpy/renpy-8.0.3-sdk/renpy.sh . demotools call=my_demo_label
# Run a specific label and loop
../../../sdk/renpy/renpy-8.0.3-sdk/renpy.sh . demotools call=my_demo_label loop
# Run a specific label and create render snapshots
../../../sdk/renpy/renpy-8.0.3-sdk/renpy.sh . demotools --render call=my_demo_label
```

## Available commands

Most commands take a value declared with `=`, optionnal arguments are between `[]`.

Nearly all parameters accept an optional `DELAY` parameter that specifies how long to wait before performing the action.

* `call=LABEL_NAME[:DELAY]`: Call a label
  * `LABEL_NAME`: The name of the label that should be called
* `show=SCREEN_NAME[:DELAY]`:
  * `SCREEN_NAME`: The name of the screen that should be shown
* `cursor=POS_X:POS_Y[:TIME[:DELAY]]`': Set the cursor's position
  * `POS_X`, `POS_Y`: Cursor's position
  * `TIME`: How long it takes for the cursor to move to its new position
* `loop[=DELAY]`: Restart command sequence from the start. DO NOT USE WHEN RENDERING
* `quit[=DELAY]`: Explicitly stop Ren'Py. This is inserted by default at the end of processing.
* `pause[=DELAY]`: Add an explicit delay before processing the next command
