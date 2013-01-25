# -*- coding: utf-8 -*-
# import from standard library
import timeit
import numpy as np
import random
#---------------------------------------------------------
# TEST DATA VARIABLES
#---------------------------------------------------------
POW = 4
# computational region: ROWSxCOLS
ROWS = 10 ** POW
COLS = 10 ** POW
# vector inputs parameters
VNAME = 'points%02d'
NPOINTS = 10 ** POW
NVECT = 5
VNAMES = [VNAME % i for i in xrange(NVECT)]
SEEDS = [random.randint(0, 100000) for i in xrange(NVECT)]
# raster inputs parameters
RNAME = 'field'
# timeit parameters
REPEAT = 3
NUMBER = 1
#
CREATE = False
#---------------------------------------------------------
# import from grass
from grass.pygrass.modules import general as g
from grass.pygrass.modules import raster as r
from grass.pygrass.modules import vector as v


def set_mapset(vnames, rname, rows=10000, cols=10000, npoints=10000, seeds=[]):
    print "set region..."
    g.region(s='0', n=str(rows), w='0', e=str(cols), res='1', flags='p')
    print "generate random raster..."
    print '*', rname
    r.mapcalc(expression="%s = rand(0., 100.)" % rname, overwrite=True)
    print "generate vector maps..."
    for vname, seed in zip(vnames, seeds):
        print '*', vname, seed
        v.random(output=vname, n=npoints, zmin=0., zmax=100., column='height',
                 seed=seed, flags='z', overwrite=True)


def print_results(cmd, setup, times):
    print setup
    print cmd
    print "-" * 30
    print "total time: %f" % sum(times)
    print "average: %f" % np.mean(times)
    print "std dev: %f" % np.std(times)
    print "min: %f" % min(times)
    print "max: %f" % max(times)
    print times
    print "=" * 30

if CREATE:
    set_mapset(VNAMES, RNAME, ROWS, COLS, NPOINTS, SEEDS)


#
# SAMPLE
#
print "Sample"
sample_cmd = "samples(VNAMES, RNAME)"
sample_set = '''from sample_rast import samples
VNAMES = %r
RNAME = %r
''' % (VNAMES, RNAME)
sample_timer = timeit.Timer(sample_cmd, setup=sample_set)
sample_times = sample_timer.repeat(REPEAT, NUMBER)

#
# RasterRow using numpy
#
rr_cmd = "ifnumpy('field', 'test_ifnumpy')"
rr_set = "from rastrow import ifnumpy"
rr_timer = timeit.Timer(rr_cmd, setup=rr_set)
print rr_cmd
rr_times = rr_timer.repeat(REPEAT, NUMBER)

#
# RasterRow using numpy and cell
#
rrc_cmd = "ifnumpy_cell('field', 'test_ifnumpy_cell')"
rrc_set = "from rastrow import ifnumpy_cell"
rrc_timer = timeit.Timer(rrc_cmd, setup=rrc_set)
print rrc_cmd
rrc_times = rrc_timer.repeat(REPEAT, NUMBER)

#
# r.mapcalc
#
mapcalc_cmd = """sub.Popen("r.mapcalc expression='test_mapcal=if(field>50,1,0)' --o", shell=True).wait()"""
mapcalc_set = "import subprocess as sub"
mapcalc_timer = timeit.Timer(mapcalc_cmd, setup=mapcalc_set)
print mapcalc_cmd
mapcalc_times = mapcalc_timer.repeat(REPEAT, NUMBER)

#
# r.mapcalc and cell
#
mapcalcc_cmd = """sub.Popen("r.mapcalc expression='test_mapcalc=if(field>50,field,0)' --o", shell=True).wait()"""
mapcalcc_set = "import subprocess as sub"
mapcalcc_timer = timeit.Timer(mapcalcc_cmd, setup=mapcalcc_set)
print mapcalcc_cmd
mapcalcc_times = mapcalcc_timer.repeat(REPEAT, NUMBER)

#
# Mapset glist
#
glist_cmd = "Mapset('PERMANENT').glist('rast')"
glist_set = "from grass.pygrass.gis import Mapset"
glist_timer = timeit.Timer(glist_cmd, setup=glist_set)
print glist_cmd
glist_times = glist_timer.repeat(REPEAT, NUMBER * 10)

#
# Mapset gcore list
#
glistc_cmd = "gcore.list_grouped('rast')['PERMANENT']"
glistc_set = "from grass.script import core as gcore"
glistc_timer = timeit.Timer(glistc_cmd, setup=glistc_set)
print glistc_cmd
glistc_times = glistc_timer.repeat(REPEAT, NUMBER * 10)

#
# Region to dict
#
reg_cmd = "dict(Region().iteritems())"
reg_set = "from grass.pygrass.gis.region import Region"
reg_timer = timeit.Timer(reg_cmd, setup=reg_set)
print reg_cmd
reg_times = reg_timer.repeat(REPEAT, NUMBER * 10)

#
# Region gcore to dict
#
regc_cmd = "gcore.region()"
regc_set = "from grass.script import core as gcore"
regc_timer = timeit.Timer(regc_cmd, setup=regc_set)
print regc_cmd
regc_times = regc_timer.repeat(REPEAT, NUMBER * 10)

#---------------------------------------------------------
# Print results
#
print_results(sample_cmd, sample_set, sample_times)
print_results(rr_cmd, rr_set, rr_times)
print_results(rrc_cmd, rrc_set, rrc_times)
print_results(mapcalc_cmd, mapcalc_set, mapcalc_times)
print_results(mapcalcc_cmd, mapcalcc_set, mapcalcc_times)
print_results(glist_cmd, glist_set, glist_times)
print_results(glistc_cmd, glistc_set, glistc_times)
print_results(reg_cmd, reg_set, reg_times)
print_results(regc_cmd, regc_set, regc_times)
