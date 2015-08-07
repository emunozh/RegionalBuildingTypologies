#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Fri May 22 2015

"""

from pandas import HDFStore
from random import choice, seed
import pandas as pd
import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
# Import internal libraries
from root.EPidf.Functions import getHL
from root.GeoData.GIS_key import DAF_key
# finds a matching material in the MASEA database
from scripts.fetchMaterial import getMasea
# Connection to dbs
from scripts.MASEA import getData_masea
from scripts.OEKOBAU import getData_oeko
# Load the R library.
HEAT = importr('heat')

# Global variables
seed(12345)
store = HDFStore('materials.h5')
D = store["elements"]
# Definition of possible construction periods as define in the regional
# material catalogue.
years = ["bis 1918", "bis 1948", "1949 bis 1957",
         "1958 bis 1968", "1969 bis 1978"]

masea = getData_masea()
MASEA = masea[(masea.name == "Steinwolle_60") | (masea.name == "EPS_040.15") |
              (masea.name == "XPS_Deckschicht 3")]

oeko = getData_oeko()
OEKO = oeko[([((("WDVS" in o_name) & ("Steinwolle" in o_name)) |
               (("WDVS" in o_name) & ("EPS" in o_name) &
                ("Daemmplatte" in o_name)) &
               ("End of life" not in o_name) | ("XPS" in o_name))
            for o_name in oeko.name])]


def get_masea_uval(component, verbose=False):
    """Get MASEA based u-value for given component."""
    if verbose:
        print(component)
    MaterialsToGet = robjects.StrVector(component["name"].tolist())
    Thicknes = robjects.FloatVector(component["Thickness"].div(100).tolist())
    Layers = HEAT.getLayers(MaterialsToGet, Thicknes)
    if verbose:
        print("Layers for HEAT.calculateUval:", [a[0] for a in Layers])
    uval = HEAT.calculateUval(Layers)
    return(uval)


def get_insulation_layer(retrofit, verbose=False):
    """create insulation layer based on retrofot option."""
    if retrofit == 1:  # Steinwolle_60 12
        if verbose:
            print("adding 12cm of Steinwolle_60 to component")
        L = MASEA.loc[69, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 12
    elif retrofit == 2:  # Steinwolle_60 24
        if verbose:
            print("adding 24cm of Steinwolle_60 to component")
        L = MASEA.loc[69, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 24
    elif retrofit == 3:  # XPS 82
        if verbose:
            print("adding 12cm of XPS to component")
        L = MASEA.loc[82, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 12
    elif retrofit == 4:  # XPS 82
        if verbose:
            print("adding 24cm of XPS component")
        L = MASEA.loc[82, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 24
    elif retrofit == 5:  # EPS 165
        if verbose:
            print("adding 12cm of EPS component")
        L = MASEA.loc[165, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 12
    elif retrofit == 6:  # EPS 165
        if verbose:
            print("adding 24cm of EPS component")
        L = MASEA.loc[165, ["name", "DenV", "ConducV", "HeatV", "DiffV"]]
        L["Thickness"] = 24
    return(pd.DataFrame(L))


def get_retrofit(layers, retrofit, verbose=False):
    """add insulation to layers."""
    if verbose:
        print("!get retrofit!")
    insulation_layer = get_insulation_layer(retrofit, verbose=verbose)
    if verbose:
        print("adding layer:")
        print(insulation_layer)
    new_layers = pd.concat([insulation_layer.T, layers])
    if verbose:
        print("All layers:")
        print(new_layers)
    return(new_layers)


def get_element(year, element_type, flat_roof=False,
                location="22", iteration=1, weight=10,
                verbose=False, force_inx=False, force_ite=False,
                print_layers=False, retrofit=False):
    """Function *get_element* retrieves a building component from the catalogue
    based on: 1. location 2. construction year 3. building component type

    The parameter *location* is define as a string containing the location code
    from the regional material catalogue. The parameter *year* is define as an
    integer between defining the construction year of the building. The
    *building component type* parameter distinguish between two building
    components: (a) *wall* and (b) *roof*. the regional material catalogue
    identifies more component types, these other component types haven't been
    implemented yet into the source code."""
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
            & ["k.A." not in a for a in D["Uval"]]]
        if building_components.shape[0] == 0:
            year = years[years.index(year) + 1]
            if verbose:
                print(
                    "could't find a matching component\
                            with following characteristics:")
                print("Location: ", location)
                print("Year: ", year)
                print("Type: ", element_type_de)
                print("U-val != k.A.")
        else:
            found = True
    inx = choice([i for i in range(building_components.shape[0])])
    if verbose or print_layers:
        print("building components found:")
        print(building_components.iloc[inx, :])
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
        if retrofit:
            layers = get_retrofit(layers, retrofit, verbose=verbose)
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
            layers_out = layers
        if force_ite:
            break
    if print_layers:
        print(layers_out)
    index = pd.MultiIndex.from_tuples([(year, element_type)],
                                      names=['year', 'typ'])
    uvalues = pd.DataFrame({"masea": Uval_masea,
                            "catalogue": Uval_catal}, index=index)
    return(uvalues)


def get_year_index(year, verbose=False):
    """ Function *get_year_index* gets the index of list *years* based on an
    input year of data type integer."""
    if verbose:
        print("get year period for year {} of type {}".format(
            year, type(year)))
    if year > 1978:
        raise Exception("year must be lower than 1979, got {}".format(year))
    years_I = []
    for y in years:
        year_interval = y.replace(" bis", "").replace(
            "bis", "0").strip().split(" ")
        years_I.append([int(i) for i in year_interval])
    years_I = pd.DataFrame(years_I, columns=["min_year", "max_year"])
    if verbose:
        print(years_I)
    sel_year = ((year >= years_I["min_year"])
                & (year <= years_I["max_year"])).tolist()
    return(years[sel_year.index(True)])


def get_components(year, flat_roof=False, iteration=1, verbose=False,
                   retrofit=False, force_inx=False, force_ite=False):
    """Function *get_components* calls the other functions and outputs a
    python dictionary containing the corresponding building components (in this
    case *wall* and *roof*). Each building component has a list with all the
    corresponding material layers of each building component and the original
    u-value from the catalogue. The function takes the construction year as
    input.

    """
    i = get_year_index(year, verbose=verbose)
    if verbose:
        print("#"*30)
        print("\tWALL")
        print("#"*30)
    uvalues = get_element(i, "wall", flat_roof=flat_roof,
                          retrofit=retrofit, iteration=iteration,
                          verbose=verbose, force_inx=force_inx,
                          force_ite=force_ite)
    if verbose:
        print("#"*30)
        print("\tROOF")
        print("#"*30)
    uval_r = get_element(i, "roof", flat_roof=flat_roof,
                         retrofit=retrofit, iteration=iteration,
                         verbose=verbose, force_inx=force_inx,
                         force_ite=force_ite)
    uvalues = uvalues.append(uval_r)
    return(uvalues)


def get_uval_components(year, flat_roof=False, verbose=False, retrofit=False):
    if verbose:
        print(year)
    c = get_components(int(year), flat_roof=flat_roof,
                       iteration=1, verbose=verbose, retrofit=retrofit)
    c_w = c.ix[0][1]
    c_r = c.ix[1][1]
    return(c_w, c_r)


def print_var(var_name, var):
    if isinstance(var, float) or isinstance(var, np.float):
        print("\t{:<13} {:0.3f} -- {}".format(var_name, var, type(var)))
    elif isinstance(var, list):
        for v in var:
            print("\t{:<13} {:0.3f} -- {}".format(var_name, v, type(v)))
    else:
        print("\t{:<13} {:>4} -- {}".format(var_name, var, type(var)))


def get_heat(row, verbose=False, retrofit=False):
    roof_slope = DAF_key[int(row["daf"])][-1]
    if roof_slope == 0:
        fr = True
    else:
        fr = False
    if verbose:
        print("flatt roof: ", fr)
    c_w, c_r = get_uval_components(row["bja"], flat_roof=fr,
                                   verbose=verbose, retrofit=retrofit)
    HL = getHL(row["SimpleGeometry"])
    Bdim = robjects.FloatVector([HL[0], HL[1]])
    h = int(row["aog"] * 3)
    sqm = row["sqm"]
    if verbose:
        print("&"*30)
        print("--ESTIMATING HEAT--")
        print("&"*30)
        print("\tINPUT:")
        print_var("uval wall", c_w)
        print_var("uval roof", c_r)
        print("Bdim: ", Bdim)
        print_var("h", h)
        print_var("sqm", sqm)
    Qhs = HEAT.heat(
        building_uvalw=c_w,
        building_uvalr=c_r,
        building_dim=Bdim,
        building_h=h,
        building_roofslope=int(roof_slope),
        )[-2][0]
    if verbose:
        print("&"*30)
        print("--DONE--")
        print("&"*30)
    if verbose:
        print("Estimated heat demand: {} of type: {}".format(Qhs, type(Qhs)))
    Qh = Qhs * sqm
    return(Qh)
