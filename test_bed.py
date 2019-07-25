import concurrent.futures
import time


def thread_function1(name):
    print(f'{name} starts')
    while True:
        time.sleep(1)
        print(f'{name} running every second')


def thread_function2(name):
    print(f'{name} starts')
    while True:
        time.sleep(10)
        print(f'{name}  every 10 seconds')


def thread_function3(name):
    print(f'{name} starts')
    while True:
        time.sleep(30)
        print(f'{name} 30 seconds')


with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(thread_function1, 1)
    executor.submit(thread_function2, 2)
    executor.submit(thread_function3, 3)
    executor.shutdown()
