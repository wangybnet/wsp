# coding=utf-8

from xmlrpc.client import ServerProxy

if __name__ == "__main__":
    client =  ServerProxy("http://192.168.120.181:7310")
    tasks = client.running_tasks()
    print(tasks)
    for task_id in tasks:
        print(client.task_info(task_id))
        print(client.task_progress(task_id))
