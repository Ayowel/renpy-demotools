label start:
    call context_test
    $ renpy.quit()

label context_test:
    show ic1 at pos1
    "Début"
    #show azeazeazhe at top
    show ic2 at pos2
    c2 "Bonjour"
    c2 "Bonjour"
    c1 "Ceci est un test"
    c1 "Bonjour"
    return

label context_test_2:
    show ic1 at pos2
    show ic2 at pos1
    c2 "Test 2"
    c2 "We're so happy to see you here"
    return
