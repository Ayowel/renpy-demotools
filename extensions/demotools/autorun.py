import renpy
import demotools

renpy.arguments.register_command("demotools", demotools.demotools_command, uses_display = True)
