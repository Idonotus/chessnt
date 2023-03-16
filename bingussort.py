import threading
import time
def sort(array):
    array=sorted(array)
    for _ in array:
        threading.Thread(target=sort,args=(array,),daemon=True).start()
    time.sleep(len(array)*2)
    return array
array=[1,4,0]
print(sort(array))