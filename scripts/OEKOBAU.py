#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue May 12, 2015

"""

from root.MySQL.dbData import MSdb

OEKOBAU_COLS = ["name", "TEI", "TEIunit", "unit", "RFA"]


def change_str(name):
    name = name.replace("_", " ")
    name = name.split(".")[-1]
    name = name[3:-1]
    return(name)


def getData_oeko():
    """retrieve data from MySQL database."""

    ObjData = MSdb("materials")
    oekobau = ObjData.getDataFrame("oeko", Col=",".join(OEKOBAU_COLS))
    ObjData.close()

    oekobau["name"] = oekobau["name"].apply(change_str)

    return(oekobau)


def main():
    oeko = getData_oeko()

    print(oeko.tail())

if __name__ == "__main__":
    main()
