#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue May 12, 2015

"""

from root.MySQL.dbData import MSdb
import numpy as np
import pandas as pd

MASEA_COLS = ["name", "family", "subfamily",
              "DenV", "ConducV", "HeatV", "DiffV"]


def getData_masea():
    """retrieve data from MySQL database."""

    ObjData = MSdb("materials")
    masea = ObjData.getDataFrame("masea", Col=",".join(MASEA_COLS))
    ObjData.close()

    extra_col = ['n.a', 'n.a', 'n.a', np.nan, np.nan, np.nan, np.nan]
    a = pd.DataFrame({"L": extra_col}).T
    a.columns = masea.columns

    masea = masea.append(a)

    return(masea)

masea_single = [("Conductivity", "ConducV")]
masea_multiple = {"Material": MASEA_COLS[0:2]}


def main():
    masea = getData_masea()

    print(masea.tail())

if __name__ == "__main__":
    main()
