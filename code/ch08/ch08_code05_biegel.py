def traffic_light():
    while True:
        print("Light is Green")
        yield "Green"

        print("Light is Yellow")
        yield "Yellow"

        print("Light is Red")
        yield "Red"


light = traffic_light()
next(light)  # Prints "Light is Green"
next(light)  # Prints "Light is Yellow"
