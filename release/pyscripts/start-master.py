# encoding: utf-8


from wsp.master.master import Master
import yaml
import sys


if __name__ == "__main__":

    global master_yaml
    master_yaml = sys.argv[1]
    def get_master_yaml():
        global master_yaml
        try:
            with open(master_yaml, "r", encoding="utf-8") as f:
                dict = yaml.load(f)
                return dict
        except Exception:
            print("Loafing master.yaml is failed")

    config = get_master_yaml()
    master = Master(config)
    master.start()


