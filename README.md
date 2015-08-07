# Regional Building Typologies

Supplementary material for a manuscript submission

It contains a set of IPython notebooks documenting the undertaken analysis
steps. A folder called `scripts` contains a collection of scripts used during
the analysis. The notebooks can be render within github of visualized at
[nbviewer](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/tree/master/).

[start here](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28a%29%20Data%20Retrival.ipynb)

The paper has been submitted to the journal
[Management of Environmental Quality: An International Journal](http://www.emeraldinsight.com/loi/meq)
and is currently under review. 

The following collection of IPython notebooks presents a short description of
the analysis performed to match different data sets regarding the material
properties of building components of an regional material catalog. These
components are attributed to buildings in a digital cadastre. Aim of this
analysis if the representation of a regional building typology for the
estimation of residential heat demand and environmental impacts of retrofits to
the building stock.

The notebooks are chronological sorted following the undertaken analysis steps.
These scripts make use of the different scripts available under the folder
called `scripts`. This collection of notebooks should serve as complementary
material to the paper with the same name. A fully reproducibility of the
results is with the provided data not possible. The used digital cadastre for
the city of Hamburg is not available for public use. The material data are
directly retrieved from an internal MySQL database, this database is not
available for public use, but the data itself is. Please contact the paper
author for further details on the used method and data.

The analysis has been divided into 7 sections, each section is represent by a
notebook:

    [(a) Data Retrival](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28a%29%20Data%20Retrival.ipynb) 
    This notebook described the algorithm used to retrive the data describing
    the regional material catalog.

    [(b) Enriching the Data](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28b%29%20Enriching%20the%20Data.ipynb)
    This notebook describes the process used to enrich the regional catalog
    with data from the
    [MASEA](http://www.masea-ensan.com/) data set and the
    [Ökobau.dat](http://www.nachhaltigesbauen.de/baustoff-und-gebaeudedaten/oekobaudat.html)
    data set.

    [(c) Constructing Typologies](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28c%29%20Constructing%20Typologies.ipynb)
    Is a description of the developed algorithm used to define building
    typologies based on the enriched building material catalog. 

    [(d) Heat Demand](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28d%29%20Heat%20Demand.ipynb)
    Implements an R package for the estimation of heat demand using information
    from the regional building typology.

    [(e) Embodied Energy](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28e%29%20Embodied%20Energy.ipynb)
    Shows the undertaken computation for the estimation of embodied energy of
    retrofits. 

    [(f) Energy Payback](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28f%29%20Energy%20Payback.ipynb)
    Presents a comparision between the estimated operational heat demand of the
    individual buildings and the estimated embodied energy of retrofit
    alternatives.

    [(g) Mapping](http://nbviewer.ipython.org/github/emunozh/RegionalBuildingTypologies/blob/master/%28g%29%20Mapping.ipynb)
    Briefly presents the implemented geometrical simplification of builiding of
    the digital cadastre for the estimation of heat demand and embodied energy.
