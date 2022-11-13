screen yesno_prompt(message = "Are you sure", yes_action = [], no_action = []):
    add "#000":
        xsize 1. ysize 1.
    vbox:
        xalign 0.5 yalign 0.5
        text message:
            xalign 0.5
        textbutton "Yes":
            xalign 0.5
            action yes_action
        textbutton "No":
            xalign 0.5
            action no_action
