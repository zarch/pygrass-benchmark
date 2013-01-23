# -*- coding: utf-8 -*-
from grass.pygrass.raster import RasterRow


def ifnumpy(mapname0, mapname1):
    # instantiate raster objects
    old = RasterRow(mapname0)
    new = RasterRow(mapname1)
    # open the maps
    old.open('r')
    new.open('w', mtype=old.mtype, overwrite=True)
    # start a cycle
    for row in old:
        new.put_row(row > 50)
    # close the maps
    new.close()
    old.close()


def ifnumpy_cell(mapname0, mapname1):
    # instantiate raster objects
    old = RasterRow(mapname0)
    new = RasterRow(mapname1)
    # open the maps
    old.open('r')
    new.open('w', mtype=old.mtype, overwrite=True)
    # start a cycle
    for row in old:
        true = row > 50
        new.put_row(row * true)
    # close the maps
    new.close()
    old.close()
