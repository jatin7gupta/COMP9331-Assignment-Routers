import time

var_not_in_loop_below = 78
counter = 0
while True:
    counter += 1
    if counter <= 1:
        dummy_text = "Dummy"
    else:
        dummy_text = "Dummies"
    print(str(counter) + " " + dummy_text)
    time.sleep(2)
    loop_var = 42
