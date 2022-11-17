# Demotools

[![Release status](https://img.shields.io/github/workflow/status/ayowel/renpy-demotools/Release?label=release)](https://github.com/Ayowel/renpy-demotools/actions/workflows/release.yml)
[![Release version](https://img.shields.io/github/v/release/ayowel/renpy-demotools)](https://github.com/Ayowel/renpy-demotools/releases/latest)
[![License](https://img.shields.io/github/license/ayowel/renpy-demotools)](LICENSE)

This is a tool used to generate live demos or demo snapshots to generate gifs

## Usage

Copy a released `demotools.rpe` into the Ren'Py game's `game` folder.
Move to the game's root directory in the command line and run the `demotools` command:

```sh
# Run a specific label and stop
renpy.sh . demotools call=my_demo_label
# Run a specific label and loop
renpy.sh . demotools call=my_demo_label loop
# Run a specific label and create render snapshots
renpy.sh . demotools --render call=my_demo_label
```

If you want to create your own gifs from the generated files, we recommend you use ffmpeg :

```sh
# Create a new snapshot 
mkdir -p target/cache
renpy.sh . demotools --render --render-fps 5 --destination target/cache call=my_demo_label
ffmpeg -v warning -f image2 -i 'target/cache/snapshot-%*.png' -framerate 5 -r 5 -y target/snapshot.gif
```

## Available commands

Most commands take a value declared with `=`, optionnal arguments are between `[]`.

Nearly all parameters accept an optional `DELAY` parameter that specifies how long to wait before performing the action.

* `call=LABEL_NAME[:DELAY]`: Call a label
  * `LABEL_NAME`: The name of the label that should be called
* `show=SCREEN_NAME[:DELAY]`:
  * `SCREEN_NAME`: The name of the screen that should be shown
* `jump=LABEL_NAME[:DELAY]`:
  * `LABEL_NAME`: The name of the label that should be jumped to
* `hidescreen=SCREEN_NAME[:DELAY]`:
  * `SCREEN_NAME`: The name of the screen that should be hidden
* `cursor=POS_X:POS_Y[:TIME[:DELAY]]`': Set the cursor's position
  * `POS_X`, `POS_Y`: Cursor's position
  * `TIME`: How long it takes for the cursor to move to its new position
* `loop[=DELAY]`: Restart command sequence from the start. DO NOT USE WHEN RENDERING
* `quit[=DELAY]`: Explicitly stop Ren'Py. This is inserted by default at the end of processing.
* `pause[=DELAY]`: Add an explicit delay before processing the next command
