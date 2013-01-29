# -*- coding: utf-8 -*-
# import from standard library
import timeit
import numpy as np
import random
import pickle
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
REPEAT = 5
NUMBER = 1
# create maps
CREATE = True
# save results
SAVE = True
RESULT = 'results.pkl'
#
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


SUMMARY = """
Sample:      {sample}s (pygrass) vs {vsample} (v.sample2)
Raster:      {rr}s (pygrass) vs {mapcalcpy}s (r.mapcalc through pygrass) vs {mapcalc}s (r.mapcalc)
Raster cell: {rrc}s (pygrass) vs {mapcalcc}s (r.mapcalc)
glist:       {glist}s (pygrass) vs {glistc}s (gcore)
region:      {reg}s (pygrass) vs {regc}s (gcore)
"""


def get_summary(fun=np.mean):
    return SUMMARY.format(sample=fun(sample_times),
                          vsample=fun(vsample_times),
                          rr=fun(rr_times),
                          mapcalcpy=fun(mapcalcpy_times),
                          mapcalc=fun(mapcalc_times),
                          rrc=fun(rrc_times), mapcalcc=fun(mapcalcc_times),
                          glist=fun(glist_times), glistc=fun(glistc_times),
                          reg=fun(reg_times), regc=fun(regc_times),)

if CREATE:
    set_mapset(VNAMES, RNAME, ROWS, COLS, NPOINTS, SEEDS)


#
# SAMPLE
#
sample_cmd = "samples(%r, %r)" % (VNAMES, RNAME)
sample_set = 'from sample_rast import samples'
sample_timer = timeit.Timer(sample_cmd, setup=sample_set)
print '\n', "=" * 40
print sample_cmd
print "=" * 40
sample_times = sample_timer.repeat(REPEAT, NUMBER)

try:
    vsample_cmd = "v_samples(%r, %r)" % (VNAMES, RNAME)
    vsample_set = 'from sample_rast import v_samples'
    vsample_timer = timeit.Timer(vsample_cmd, setup=vsample_set)
    print '\n', "=" * 40
    print vsample_cmd
    print "=" * 40
    vsample_times = vsample_timer.repeat(REPEAT, NUMBER)
    VSAMPLE = True
except:
    print "You must install and compile the GRASS module v.sample2"
    VSAMPLE = False

#
# RasterRow using numpy
#
rr_cmd = "ifnumpy('field', 'test_ifnumpy')"
rr_set = "from rastrow import ifnumpy"
rr_timer = timeit.Timer(rr_cmd, setup=rr_set)
print '\n', "=" * 40
print rr_cmd
print "=" * 40
rr_times = rr_timer.repeat(REPEAT, NUMBER)

#
# r.mapcalc using pygrass to evaluate the Module class overload
#
mapcalcpy_cmd = "r.mapcalc(expression='test_mapcal=if(field>50,1,0)', overwrite=True)"
mapcalcpy_set = "from grass.pygrass.modules import raster as r"
mapcalcpy_timer = timeit.Timer(mapcalcpy_cmd, setup=mapcalcpy_set)
print '\n', "=" * 40
print mapcalcpy_cmd
print "=" * 40
mapcalcpy_times = mapcalcpy_timer.repeat(REPEAT, NUMBER)

#
# r.mapcalc
#
mapcalc_cmd = """sub.Popen("r.mapcalc expression='test_mapcal=if(field>50,1,0)' --o", shell=True).wait()"""
mapcalc_set = "import subprocess as sub"
mapcalc_timer = timeit.Timer(mapcalc_cmd, setup=mapcalc_set)
print '\n', "=" * 40
print mapcalc_cmd
print "=" * 40
mapcalc_times = mapcalc_timer.repeat(REPEAT, NUMBER)

#
# RasterRow using numpy and cell
#
rrc_cmd = "ifnumpy_cell('field', 'test_ifnumpy_cell')"
rrc_set = "from rastrow import ifnumpy_cell"
rrc_timer = timeit.Timer(rrc_cmd, setup=rrc_set)
print '\n', "=" * 40
print rrc_cmd
print "=" * 40
rrc_times = rrc_timer.repeat(REPEAT, NUMBER)

#
# r.mapcalc and cell
#
mapcalcc_cmd = """sub.Popen("r.mapcalc expression='test_mapcalc=if(field>50,field,0)' --o", shell=True).wait()"""
mapcalcc_set = "import subprocess as sub"
mapcalcc_timer = timeit.Timer(mapcalcc_cmd, setup=mapcalcc_set)
print '\n', "=" * 40
print mapcalcc_cmd
print "=" * 40
mapcalcc_times = mapcalcc_timer.repeat(REPEAT, NUMBER)

#
# Mapset glist
#
glist_cmd = "Mapset('PERMANENT').glist('rast')"
glist_set = "from grass.pygrass.gis import Mapset"
glist_timer = timeit.Timer(glist_cmd, setup=glist_set)
print '\n', "=" * 40
print glist_cmd
print "=" * 40
glist_times = glist_timer.repeat(REPEAT, NUMBER * 10)

#
# Mapset gcore list
#
glistc_cmd = "gcore.list_grouped('rast')['PERMANENT']"
glistc_set = "from grass.script import core as gcore"
glistc_timer = timeit.Timer(glistc_cmd, setup=glistc_set)
print '\n', "=" * 40
print glistc_cmd
print "=" * 40
glistc_times = glistc_timer.repeat(REPEAT, NUMBER * 10)

#
# Region to dict
#
reg_cmd = "dict(Region().iteritems())"
reg_set = "from grass.pygrass.gis.region import Region"
reg_timer = timeit.Timer(reg_cmd, setup=reg_set)
print '\n', "=" * 40
print reg_cmd
print "=" * 40
reg_times = reg_timer.repeat(REPEAT, NUMBER * 10)

#
# Region gcore to dict
#
regc_cmd = "gcore.region()"
regc_set = "from grass.script import core as gcore"
regc_timer = timeit.Timer(regc_cmd, setup=regc_set)
print '\n', "=" * 40
print regc_cmd
print "=" * 40
regc_times = regc_timer.repeat(REPEAT, NUMBER * 10)

#---------------------------------------------------------
# Print results
#

print 'summary mean:'
print get_summary()

print 'summary std:'
print get_summary(np.std)


print '#' * 30
print_results(sample_cmd, sample_set, sample_times)
if VSAMPLE:
    print_results(vsample_cmd, vsample_set, vsample_times)

print '#' * 30
print_results(rr_cmd, rr_set, rr_times)
print_results(mapcalcpy_cmd, mapcalcpy_set, mapcalcpy_times)
print_results(mapcalc_cmd, mapcalc_set, mapcalc_times)

print '#' * 30
print_results(rrc_cmd, rrc_set, rrc_times)
print_results(mapcalcc_cmd, mapcalcc_set, mapcalcc_times)

print '#' * 30
print_results(glist_cmd, glist_set, glist_times)
print_results(glistc_cmd, glistc_set, glistc_times)

print '#' * 30
print_results(reg_cmd, reg_set, reg_times)
print_results(regc_cmd, regc_set, regc_times)

if SAVE:
    output = open(RESULT, 'wb')
    # Pickle the list using the highest protocol available.
    data = (sample_times, vsample_times, rr_times, mapcalcpy_times,
            mapcalc_times, rrc_times, mapcalcc_times,
            glist_times, glistc_times, reg_times, regc_times)
    for d in data:
        pickle.dump(d, output, -1)
    output.close()
