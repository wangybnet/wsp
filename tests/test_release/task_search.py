# coding=utf-8

from xmlrpc.client import ServerProxy

if __name__ == "__main__":
    client =  ServerProxy("http://192.168.120.181:7310")
    tasks = client.running_tasks()
    print("running_tasks: %s" % tasks)
    for task_id in tasks:
        print("task_info: %s" % client.task_info(task_id))
        print("task_progress: %s" % client.task_progress(task_id))
