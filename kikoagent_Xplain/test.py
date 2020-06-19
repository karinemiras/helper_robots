from threading import Semaphore
sem = Semaphore(0)
print(sem._value)


if(sem.acquire(blocking=False)):
    print('blokcs')