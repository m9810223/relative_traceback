# relative_traceback

```console
$ python without_relative_traceback.py 

Traceback (most recent call last):
  File "/absolute/path/to/without_relative_traceback.py", line 1, in <module>
    1 / 0
ZeroDivisionError: division by zero


$ python with_relative_traceback.py 

Traceback (most recent call last):
  File "./with_relative_traceback.py", line 5, in <module>
    1 / 0
ZeroDivisionError: division by zero

```
