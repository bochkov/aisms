import multiprocessing

bind = "unix:/tmp/gunicorn.aisms.sock"
workers = multiprocessing.cpu_count() * 2 + 1
