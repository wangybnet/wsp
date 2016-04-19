# coding=utf-8

from bson import ObjectId
from pymongo import MongoClient


if __name__ == "__main__":
    id = "571401503fd22825435eb82d"
    tbl_name = "acm"

    client = MongoClient("mongodb://wsp:wsp123456@192.168.120.90:27017")
    tbl = client["ScholarInfoBase"][tbl_name]
    obj_dict = tbl.find_one({"_id": ObjectId(id)})
    with open("D:/%s.html" % tbl_name, "wb") as f:
        f.write(obj_dict["body"])
