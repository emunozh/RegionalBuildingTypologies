#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Fri May 22 2015

"""

import pandas as pd
import random
# internal
from root.GeoData.OwnDef import StatGebWilhemsburg
from root.DataTypes.CSV import CSV
from scripts.heat import get_heat
from scripts.OEKOBAU import getData_oeko
from scripts.MASEA import getData_masea


def computeHeat(buildings,
                file_name="buildings_heat.csv",
                file_path="./"):
    """Estimate heat demand for all building in the data frame."""
    obj = CSV(file_path, file_name)

    buildings = buildings[
        [st in StatGebWilhemsburg for st in buildings["statistical area"]]]
    b_dim = buildings.shape[0]

    cols = buildings.columns.tolist()
    cols.append("heat")
    obj.writeLine(cols)
    for i in range(b_dim):
        heat = get_heat(buildings.iloc[i], verbose=False)
        print("{:>4} / {:<4} --> {:0.2f}kWh/m2a for year {}".format(
            i, b_dim, heat/buildings.iloc[i]["sqm"], buildings.iloc[i]["bja"]))
        val = buildings.iloc[i].tolist()
        val.append(heat)
        obj.writeLine(val)


def retrofits(retrofit):
    """make retrofits."""

    obj = CSV("./", "buildings_heat_retrofit{}.csv".format(retrofit))

    buildings = pd.read_csv("buildings.csv", index_col=0)
    buildings = buildings.dropna()

    buildings = buildings[
        [st in StatGebWilhemsburg for st in buildings["statistical area"]]]
    buildings['heat'] = 0

    # sample_size = int(buildings.shape[0] * 0.01)
    sample_size = int(buildings.shape[0] * 0.1)
    print("sample size = ", sample_size)
    random.seed(12345)
    rows = random.sample(buildings.index.tolist(), sample_size)
    buildings = buildings.ix[rows]

    b_dim = buildings.shape[0]

    cols = buildings.columns.tolist()
    cols.append("heat")
    obj.writeLine(cols)
    for i in range(b_dim):
        heat = get_heat(buildings.iloc[i], verbose=False, retrofit=retrofit)
        print("{:>4} / {:<4} --> {:0.2f}kWh/m2a for year {} - s {}".format(
            i, b_dim, heat/buildings.iloc[i]["sqm"], buildings.iloc[i]["bja"],
            retrofit))
        val = buildings.iloc[i].tolist()
        val.append(heat)
        obj.writeLine(val)


def getGEnergy(buildings, pos1, pos2, width, name, verbose=False):
    if verbose:
        print("{} insulation -- width: {}".format(name, width))
        print("\t unit: {} \t TEI: {} {} \t Den: {} kg/m3".format(
            pos1["unit"], pos1["TEI"], pos1["TEIunit"],
            pos2["DenV"]))
    var_name = "{}_{:.0f}cm".format(name, width * 100)
    if pos1["TEIunit"] != "MJ":
        raise Exception("Unknown energy unit: ", pos1["TEIunit"])
    if pos1["unit"] == "kg":
        buildings[var_name] = buildings["shell"] *\
            width * pos2["DenV"] * pos1["TEI"]
    elif pos1["unit"] == "m2":
        buildings[var_name] = buildings["shell"] * width * pos1["TEI"]
    else:
        raise Exception("Unknow reference unit: ", pos1["unit"])

    return(buildings)


def computeEmbodiedEnergy():
    """Compute the embodied energy of buildings in file buildings.csv."""

    oeko = getData_oeko()
    OEKO = oeko[([((("WDVS" in o_name) & ("Steinwolle" in o_name)) |
                (("WDVS" in o_name) & ("EPS" in o_name) &
                    ("Daemmplatte" in o_name)) &
                ("End of life" not in o_name) | ("XPS" in o_name))
        for o_name in oeko.name])]

    masea = getData_masea()
    MASEA = masea[(masea.name == "Steinwolle_60") |
                  (masea.name == "EPS_040.15") |
                  (masea.name == "XPS_Deckschicht 3")]

    buildings = pd.read_csv("buildings.csv", index_col=0)
    buildings["shell_roof"] = buildings["shell"] - buildings["shell_wall"]

    for a, b, c in zip([610, 480, 482],
                       [69, 82, 165],
                       ["Steinwolle", "XPS", "EPS"]):
        pos1 = OEKO.loc[a]
        pos2 = MASEA.loc[b]
        for width in [0.12, 0.24]:
            buildings = getGEnergy(buildings, pos1, pos2, width, c,
                                   verbose=False)

    buildings.to_csv("buildings_genergy.csv")


def main():
    buildings = pd.read_csv("buildings.csv", index_col=0)
    buildings = buildings.dropna()
    computeHeat(buildings)


if __name__ == "__main__":
    main()
