# -*- coding: utf-8 -*-
import numpy as np
from grass.pygrass.gis.region import Region
from grass.pygrass.vector import VectorTopo
from grass.pygrass.raster import RasterRow
from grass.pygrass.functions import coor2pixel


def sample(vect_in_name, rast_in_name):
    """sample('point00', 'field')"""
    # instantiate the object maps
    vect_in = VectorTopo(vect_in_name)
    rast_in = RasterRow(rast_in_name)
    vect_out = VectorTopo('test_' + vect_in_name)
    # define the columns of the attribute table of the new vector map
    columns = [(u'cat',       'INTEGER PRIMARY KEY'),
               (rast_in_name,  'DOUBLE')]
    # open the maps
    vect_in.open('r')
    rast_in.open('r')
    vect_out.open('w', tab_cols=columns, link_driver='sqlite')
    # get the current region
    region = Region()
    # initialize the counter
    counter = 0
    data = []
    for pnt in vect_in.viter('points'):
        counter += 1
        # transform the spatial coordinates in row and col value
        x, y = coor2pixel(pnt.coords(), region)
        value = rast_in[int(x)][int(y)]
        data.append((counter, None if np.isnan(value) else float(value)))
        # write the geometry features
        vect_out.write(pnt)
    # write the attributes
    vect_out.table.insert(data, many=True)
    vect_out.table.conn.commit()
    # close the maps
    vect_in.close()
    rast_in.close()
    vect_out.close()


def samples(vect_in_names, rast_in_name):
    """samples(['points00', 'points01'], 'field')"""
    for vect_in in vect_in_names:
        sample(vect_in, rast_in_name)
