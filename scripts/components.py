#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Fr 07 Aug 2015 15:20:08 AEST

"""

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
heat = importr('heat')
from pandas import HDFStore
from random import choice
from random import seed
import pandas as pd
import numpy as np
# internal libs
from scripts.fetchMaterial import getMasea
# globals
years = ["bis 1918", "bis 1948", "1949 bis 1957",
         "1958 bis 1968", "1969 bis 1978"]

store = HDFStore('materials.h5')
D = store["elements"]

seed(12345)


def get_masea_uval(component, verbose=False):
    """get u-value from mases data set."""
    MaterialsToGet = robjects.StrVector(component["name"].tolist())
    Thicknes = robjects.FloatVector(component["Thickness"].div(100).tolist())
    Layers = heat.getLayers(MaterialsToGet, Thicknes)
    if verbose:
        print("Layers for heat.calculateUval:", [a[0] for a in Layers])
    uval = heat.calculateUval(Layers)
    return(uval)


def get_element(year, element_type, flat_roof=False,
                location="22", iteration=1, weight=10,
                verbose=False, force_inx=False, force_ite=False):
    """get building element."""
    if element_type == "wall":
        element_type_de = "Außenwand"
    elif element_type == "roof":
        if flat_roof:
            element_type_de = "Flachdach"
        else:
            element_type_de = "Steildach"
    else:
        raise Exception(
            "element type not implemented yet, expeced 'wall' or 'roof'")
    found = False
    while not found:
        building_components = D[
            ([location in a for a in D["Location"]])
            & (D["Year"] == year)
            & (D["Type"] == element_type_de)
            & ["k.A." not in a for a in D["Uval"]]
        ]
        if building_components.shape[0] == 0:
            year = years[years.index(year) + 1]
            if verbose:
                print("could't find a matching component\
                        with following characteristics:")
                print("Location: ", location)
                print("Year: ", year)
                print("Type: ", element_type_de)
                print("U-val != k.A.")
        else:
            found = True
    if verbose:
        print("building components found:")
        print(building_components.shape)
        print(building_components)
    inx = choice([i for i in range(building_components.shape[0])])
    Uval_diff = np.Inf
    uvalues = pd.DataFrame(columns=["masea", "catalogue"])
    for ite in range(iteration):
        if force_ite:
            ite = force_ite
        if verbose:
            print("+"*30)
            print("iteration: ", ite)
            print("+"*30)
        layers = getMasea(building_components, weight=weight,
                          iterations=iteration, component_index=inx,
                          verbose=verbose, force_index=force_inx)
        Uval_catal_temp = max(building_components.iloc[inx, 6])
        layers = layers.drop_duplicates('name')
        layers = layers[[i != "-" for i in layers.Thickness]]
        layers = layers.reindex(index=layers.index[::-1])
        try:
            Uval_masea_temp = get_masea_uval(layers, verbose=verbose)[0]
        except:
            if verbose:
                print("can't compute u-val")
            Uval_masea_temp = np.Inf
        this_diff = abs(Uval_catal_temp - Uval_masea_temp)
        if this_diff < Uval_diff:
            Uval_diff = this_diff
            Uval_masea = Uval_masea_temp
            Uval_catal = Uval_catal_temp
        if force_ite:
            break
    index = pd.MultiIndex.from_tuples(
        [(year, element_type)], names=['year', 'typ'])
    uvalues = pd.DataFrame({"masea": Uval_masea,
                            "catalogue": Uval_catal}, index=index)
    return(uvalues)


def get_year_index(year):
    """get year index."""
    if year > 1978:
        raise Exception("year must be lower than 1979, got {}".format(year))
    years_I = []
    for y in years:
        year_interval = y.replace(
            " bis", "").replace("bis", "0").strip().split(" ")
        years_I.append([int(i) for i in year_interval])
    years_I = pd.DataFrame(years_I, columns=["min_year", "max_year"])
    sel_year = ((year >= years_I["min_year"]) &
                (year <= years_I["max_year"])).tolist()
    return(years[sel_year.index(True)])


def get_components(year, flat_roof=False, iteration=1,
                   verbose=False, force_inx=False, force_ite=False):
    """Contruct building components."""
    i = get_year_index(year)
    if verbose:
        print("#"*30)
        print("\tWALL")
        print("#"*30)
    uvalues = get_element(i, "wall", flat_roof=flat_roof, iteration=iteration,
                          verbose=verbose, force_inx=force_inx,
                          force_ite=force_ite)
    if verbose:
        print("#"*30)
        print("\tROOF")
        print("#"*30)
    uval_r = get_element(i, "roof", flat_roof=flat_roof, iteration=iteration,
                         verbose=verbose, force_inx=force_inx,
                         force_ite=force_ite)
    uvalues = uvalues.append(uval_r)
    return(uvalues)
