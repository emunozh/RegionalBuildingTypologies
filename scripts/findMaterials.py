#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Tue May 12, 2015

"""

from pandas import HDFStore
import numpy as np
store = HDFStore('materials.h5')
#
materials = store.materials

MIN_L = 3


def getSingleCount(material_pos, dataset, pair, verbose=False):
    value_is_fit = materials[pair[0]][material_pos]
    if verbose:
        print("value to fit: ", value_is_fit)
    try:
        value_is_fit = float(value_is_fit)
    except:
        return(False)
    value_to_fit = dataset[pair[1]].tolist()
    Q = abs(np.asarray(value_to_fit) - value_is_fit)
    # Q = [abs(value_is_fit - b) for b in value_to_fit]
    # Q = np.asarray(Q)
    # import ipdb; ipdb.set_trace() # BREAKPOINT
    return(Q)


def _countL(material_input, dat_lower):
    # print(material_input, dat_lower)
    r = 0
    material_input = material_input.lower()
    if " " in material_input:
        materials = material_input.split(" ")
    elif "_" in material_input:
        materials = material_input.split("_")
    else:
        materials = [material_input]

    for material_i in materials:
        for sep in range(MIN_L, len(material_i)+1):
            lett = 0
            for start_l in range(len(material_i)):
                for i in range(start_l, len(material_i)+1, sep):
                    if i+sep <= len(material_i):
                        max_let = i+sep
                        if material_i[i:max_let] in dat_lower:
                            lett = sep
            r += lett
    return(r)


def countLetters(material_i, multiple_elements, dat,
                 extra=False, verbose=False):
    r = 0
    material_i = material_i.lower()
    for col in multiple_elements:
        dat_lower = dat[1][col].lower()
        r += _countL(material_i, dat_lower)

    return(r)


def getMaterialIndex(material_pos, dataset, sample=10, w=1,
                     single=False, multiple=False, verbose=False,
                     extra=False, omit=False):
    """Find the index of matching materials."""

    if verbose:
        print("getting material on pos: {}".format(material_pos))

    if verbose and extra:
        print("using {} as extra search criteria".format(extra))

    if "Luft" in materials.ix[material_pos, 0]:
        if verbose:
            print("Luft")
        return("L")

    # Compute Q (Conductivity)
    Q = np.asanyarray([0.0]*dataset.shape[0])
    if single:
        for s in single:
            if verbose:
                print("fitting: ", s[0])
            Q += getSingleCount(material_pos, dataset, s, verbose=verbose)

    if verbose and single:
        ipp = [a for a in np.where(Q == min(Q))[0]]
        if len(ipp) > 1:
            ipp = ipp[0]
        print("best match by conductivity: ", dataset.ix[ipp, 0])

    if np.nansum(Q) == 0:
        if verbose and single:
            print("Q = 0")
        if single:
            return("L")

    # Compute R (name)
    R = np.asarray([0.0]*dataset.shape[0])
    if multiple:
        for multi_key in multiple:
            material_i = materials[multi_key][material_pos]
            if verbose:
                print("searching for: ", material_i)
            R_temp = []
            r = 0
            for dat in dataset.iterrows():
                r = countLetters(
                    material_i, multiple[multi_key], dat)
                if extra:
                    for ex in extra:
                        r += countLetters(
                            ex, multiple[multi_key], dat)
                if omit:
                    for om in omit:
                        omm_lett = countLetters(
                            om, multiple[multi_key], dat)
                        if verbose:
                            print(r, "-", omm_lett)
                        if omm_lett >= r:
                            r = 0
                        else:
                            r -= omm_lett
                        if verbose:
                            print("\t= ", r)
                R_temp.append(r)
            R += np.asarray(R_temp)

    if verbose and multiple:
        ipp = [a for a in np.where(R == max(R))[0]]
        if len(ipp) > 1:
            ipp = ipp[0]
        print("best match by name: ", dataset.ix[ipp, 0])

    # Compute P
    if not single:
        if verbose:
            print("using only name")
        P = R / np.nansum(R)  # * -1
    elif np.nansum(R) == 0:
        if verbose:
            print("R = 0")
        return("L")
    else:
        # weight_multiple = sum([len(b) for _,  b in multiple.items()]) * w
        weight_multiple = w
        #Q = Q / np.nansum(Q)
        #Q = weight_multiple * Q * -1
        Q = 1 - Q / np.nansum(Q)
        R = R / np.nansum(R)
        if verbose:
            print("with weight: ", weight_multiple)
            print("sum Q --> ", np.nansum(Q) * -1)
            print("sum R --> ", np.nansum(R))
        P = weight_multiple * Q + R

    Ps = sorted(P, reverse=True)[0:sample]
    inx = []
    for p in Ps:
        for i in list(np.where(P == p)[0]):
            if i not in inx:
                inx.append(i)
    if verbose:
        print("end 'getMaterialIndex'")

    return(inx[:sample])


def main():
    from root.MySQL.dbData import MSdb

    ObjData = MSdb("materials")
    masea_cols = ["name", "family", "subfamily",
                  "DenV", "ConducV", "HeatV", "DiffV"]
    masea = ObjData.getDataFrame("masea", Col=",".join(masea_cols))
    ObjData.close()

    masea_single = [("Conductivity", "ConducV")]
    masea_multiple = {"Material": masea_cols[0:3]}

    found_data = masea.loc[getMaterialIndex(
        217, masea, w=10, single=masea_single, multiple=masea_multiple)]
    # masea.ix[getMaterialIndex(
    #     1, masea, single=masea_single, multiple=masea_multiple)]
    print(found_data)

if __name__ == "__main__":
    main()
