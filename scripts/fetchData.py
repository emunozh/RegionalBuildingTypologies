#!/usr/bin/env python
# -*- coding:utf -*-
"""
#Created by Esteban.

Fr 07 Aug 2015 14:35:55 AEST

"""

import codecs
import os
import pandas as pd
import numpy as np


# GLOBAL Parameters
a1 = """<DIV class="light" """
b1 = """<DIV class="fett" """

a2 = """STYLE="position: absolute;"""

c = """STYLE="color:#FFF; font-size:20px; position: absolute; left:122px; top:129px; width: 613px; height: 50px;"><strong>"""

e = """eft:565px; top:185px; width: 203px; font-size:18px; color:#FFFFFF; height: 45px;">"""
f = """left:565px; top:234px; width: 202px; height: 43px; font-size:18px; color:#FFFFFF;">"""
a = """eft:503px; font-size:18px; color:#FFFFFF; top:999px; width: 279px; height: 36px;">"""
g = """left:565px; top:283px; width: 198px; height: 35px; font-size:18px; color:#FFFFFF;">"""
h = """left:565px; top:425px; width: 220px; height: 38px; font-size:18px; color:#FFFFFF;">"""
k = """left:420px; top:992px; width: 79px; height: 30px; font-size:16px; padding-top:7px;">U-Wert<br>[W/(m&sup2;K)]"""
l = """left:256px; font-size:14px; color:#FFFFFF; top:1065px; width: 520px; height: 35px;">"""
i1 = """left:421px; font-size:10px; color:#FFFFFF; top:556px; width: 361px; height: 313px; padding-right: 10px; padding-left: 10px; padding-top: 10px;">\n<table border="1" cellpadding="5" cellspacing="0" style="border: solid 2px white; font-size: 15px;" width="341"><tr style="font-weight:normal;"><td>Material<br/>\xa0</td><td>Stärke<br/>[cm]</td><td>Rohdichte<br/>[kg/m³]</td><td>λ-Wert<br/>[W/(mK)]</td></tr>\n<tr><td style="border-color:#FFFFFF;border-style: solid;">"""

i2 = """</td><td style="border-color:#FFFFFF;border-style: solid;"""
i4 = """</td><td style="border-width:1px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""
i46 = """</td><td style="border-width:1px;border-color:#FFFFFF;border-style: solid;"""
i6 = """</td><td style="border-width:0px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""

i3 = """</td></tr><tr><td style="border-width:1px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""
i5 = """</td></tr><tr><td style="border-width:0px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""
i7 = """</td></tr></table><span style="font-size:16px;font-weight:normal;"></span>"""
i72 = """</td></tr>"""

i22 = """<tr ><td style="border-color:#FFFFFF;border-style: solid;"""
i42 = """<tr ><td style="border-width:1px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""
i43 = """<tr ><td style="border-width:0px 1px 0px 1px;border-color:#FFFFFF;border-style: solid;"""
i45 = """<tr ><td style="border-width:1px;border-color:#FFFFFF;border-style: solid;"""

i74 = """</table><span style="font-size:16px;font-weight:normal;"""

p1 = """"> <br> &#8226;"""
p2 = """"><br> &#8226;"""
p3 = """"><br> <br> &#8226;"""
p4 = """"><br> &bull;"""
p5 = """>&#65533;"""
p6 = """">&bull"""
ps = [p1, p2, p3, p4, p5, p6]

q1 = """">1,29</span>"""

end1 = "</DIV>"
end2 = "</strong>"
end3 = """"></span>"""


table_del_1 = [a1, b1, a2, c, e, f, a,  g, h, k, l,
               i1, i2, i4, i46, i6, i3, i5, i7, i72, i22, i42, i43, i45, i74,
               q1, end1, end2, end3]


def getHtmlData(html_doc):
    """open the html file with the proper encoding."""
    with codecs.open(
            "./html/"+html_doc, mode='r', encoding="iso-8859-15") as html_doc:
        html_data = html_doc.readlines()
    return(html_data)


def getValues(
        key_name, rep, pos, convert="f",
        html_data=False, loop=True,
        notinline=["xxx", "yyy", "zzz"]):
    """find specific values on the html file"""
    nil1 = notinline[0]
    nil2 = notinline[1]
    nil3 = notinline[2]
    if loop:
        val = key_name
        while key_name in val:
            ix_uwert = html_data.index(
                [a for a in html_data if key_name in str(a) and
                    key_name+nil1 not in str(a) and
                    key_name+nil2 not in str(a) and
                    key_name+nil3 not in str(a)][0])
            val = str(html_data[ix_uwert + pos])
            pos += 1
    else:
        ix_uwert = html_data.index(
            [a for a in html_data if key_name in str(a) and
                key_name+nil1 not in str(a) and
                key_name+nil2 not in str(a) and
                key_name+nil3 not in str(a)][0])
        val = str(html_data[ix_uwert + pos])
    for r in rep:
        val = str(val)
        val = val.replace(r, "")
    if key_name in ["U-Wert", "Postleitzahl"]:
        val = val.replace("l", "")
    if convert == "f":
        try:
            val = val.replace(",", ".").split("/")
            values = [float(a) for a in val]
        except:
            values = [str(a).strip() for a in val]
    elif convert == "s":
        values = val.strip()
    return(values)


def getComponent(html_data, html_file, ind=0):
    """get the component values from the html file."""
    if getValues("Postleitzahl",
                 [b1, c, end1, end2], 2,
                 convert="s", html_data=html_data):
        builindgComponent = pd.DataFrame([
            getValues("Postleitzahl", [b1, c, end1, end2], 2,
                      convert="s", html_data=html_data),
            getValues("Postleitzahl", [a1, a2, e, end1], 10,
                      convert="s", html_data=html_data),
            getValues("Baualters", [a1, a2, f, end1], 2,
                      convert="s", html_data=html_data),
            getValues("Bauteil", [a1, a2, g, end1], 1,
                      convert="s", html_data=html_data),
            getValues("Konstruktion", [a1, a2, h, end1], 1,
                      convert="s", html_data=html_data),
            getValues("U-Wert", [a1, a2, a, b1, k, end1], 0,
                      convert="f", html_data=html_data,
                      loop=False,
                      notinline=["es", " Varianten", " nicht berechnet"]),
            getValues("Zentrum", [a1, a2, l], 1,
                      convert="s", html_data=html_data).replace(", ,", ""),
                      str(html_file)],
            columns=[ind],
            index=["Name", "Location", "Year", "Type",
                   "Construction", "Uval", "Source", "File"])
        builindgComponent = builindgComponent.T
    else:
        builindgComponent = [False]
    return(builindgComponent)


def getData():
    """get all data into a pandas data frame."""
    material_table = pd.DataFrame(columns=[
        "Construction", "File", "Location",
        "Name", "Source", "Type", "Uval", "Year"])
    position = 0
    for html_file in os.listdir("./html"):
        html_data = getHtmlData(html_file)
        tab = getComponent(html_data, html_file, ind=position)
        if any(tab):
            position += 1
            material_table = material_table.append(tab)

    to_change_uval = []
    for a, uval in enumerate(material_table.Uval.tolist()):
        p = sum([1 for i in uval if isinstance(i, str)])
        if p > 1 or isinstance(uval[0], str):
            to_change_uval.append(a)

    for i in to_change_uval:
        new_uvals = []
        if material_table.Uval[i][0] != "k.A." and\
           material_table.Uval[i][0] != "XXXXXXX":
            for uval_str in material_table.Uval[i]:
                uvals = [float(a) for a in uval_str.split("-")]
                new_uvals.append(np.arange(min(uvals), max(uvals), 0.01))
            material_table.Uval[i] = new_uvals[0]

    return(material_table)


def chunks(l, n):
    # split list in chunks of same length
    for i in range(0, len(l), n):
        yield [i for i in l[i:i + n]]


def deleteNotes(materials):
    """get rid of notes."""
    for p in ps:
        if p in materials:
            ix = materials.index(p)
            materials = materials[0:ix]
    return(materials)


def getMaterialTable(html_data):
    """Create the table with the materials information."""
    materials = getValues("Material", table_del_1,
                          4, convert="s", html_data=html_data)
    materials = deleteNotes(materials)
    materials = materials[2:].replace(",", ".").split("""">""")
    materials_f = []
    for m in materials:
        try:
            materials_f.append(float(m))
        except:
            materials_f.append(m.strip())
    materials_table = pd.DataFrame(
        [a for a in chunks(materials_f, 4)],
        columns=["Material", "Width", "Density", "Conductivity"])

    return(materials_table)
