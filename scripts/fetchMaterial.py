#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue May 12 2015

"""

import pandas as pd
from pandas import HDFStore
from random import choice
# internal
from scripts.MASEA import getData_masea
from scripts.MASEA import masea_single
from scripts.MASEA import masea_multiple
from scripts.findMaterials import getMaterialIndex
from scripts.findMaterials import materials

store = HDFStore('materials.h5')

masea = getData_masea()


def getMasea(data_element, verbose=False, extra=False, weight=1, iterations=False, component_index=False, force_index=False):

    if not component_index:
        inx = 0
    else:
        inx = component_index
    layers = store["table_{}".format(data_element.iloc[inx, 1].split(".")[0])]
    layers.set_index("Material", inplace=True)
    thikness = layers["Width"]

    indexed_layers = pd.DataFrame(columns=[
        "Material", "Density", "Conductivity"])
    if verbose:
        print(layers)
    for layer in layers.index:
        if verbose:
            print([1 for a in layers.index if layer == a])
        if sum([1 for a in layers.index if layer == a]) > 1:
            if verbose:
                print("got more than 1 layer: ", layers.loc[layer].shape[0])
                print(layers.loc[layer])
            conduc = layers.loc[layer, "Conductivity"].ix[0]
            den = layers.loc[layer, "Density"].ix[0]
        else:
            conduc = layers.loc[layer, "Conductivity"]
            den = layers.loc[layer, "Density"]
        try:
            material_index = materials[
                (materials.Material == layer)
                & (materials.Conductivity == conduc)
                & (materials.Density == den)
                ].index.tolist()
        except:
            print("Couldn't find a material in the database")
            print("With following attributes:")
            print("\tshape: ", layers.loc[layer].shape)
            print("\tMaterial: ", layer)
            print("\tConductivity: ", layers.loc[layer, "Conductivity"])
            print("\tDensity: ", layers.loc[layer, "Density"])
            return(layers)
            #raise Exception("Couldn't find a material in the database")
        if verbose:
            print("got <{}> layer".format(layer))
        indexed_layers = indexed_layers.append(materials.ix[material_index])

    if not extra:
        extra_cri = [False] * len(indexed_layers)
    else:
        extra_cri = []
        for inx in range(len(indexed_layers)):
            if inx in extra.keys():
                extra_cri.append(extra[inx])
            else:
                extra_cri.append(False)

    if verbose:
        print("extra criteria: ", extra_cri)

    indexed_layers_masea = pd.DataFrame(columns=["name", "DenV", "ConducV", "HeatV", "DiffV", "Thickness"])
    
    for e, idx_l in enumerate(indexed_layers.index.tolist()):
        if(verbose):
            print("geting {} layer on index: {} with extra {}".format(
                indexed_layers.loc[idx_l, "Material"], idx_l, extra_cri[e]))
        if not iterations:
            sample_size = 1
        else:
            sample_size = iterations + 1
        index_material = getMaterialIndex(
            idx_l, masea, single=masea_single, sample=sample_size,
            multiple=masea_multiple, w=weight, extra=extra_cri[e],
            verbose=verbose)
        if verbose:
            print("index length = ", len(index_material))
            print("index: ", index_material)
        if not iterations:
            index_pos = 0
        else:
            index_pos = choice(range(len(index_material)))
        if force_index:
            index_pos = force_index
        if verbose:
            print("sample size = ", sample_size)
            print("index possition = ", index_pos)
        m_ix = masea.ix[[index_material[index_pos]], [0, 3, 4, 5, 6]]
        if m_ix.index == "L":
            m_ix["name"] = indexed_layers.loc[idx_l, "Material"]
            try:
                ConducV = float(indexed_layers.loc[idx_l, "Conductivity"])
                m_ix["ConducV"] = ConducV
            except:
                pass
        if verbose:
            print("masea indexd data: ", m_ix)
            print("masea indexd data - thikness: ", thikness)
            print("masea indexd data - thikness index: ", e)
        m_ix["Thickness"] = thikness.ix[e]
        indexed_layers_masea = indexed_layers_masea.append(m_ix)

    return(indexed_layers_masea)
