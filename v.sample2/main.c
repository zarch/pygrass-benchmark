/****************************************************************
 *
 * MODULE:       v.sample2 (based on v.sample)
 *
 * AUTHOR(S):    Soeren Gebbert
 *
 * COPYRIGHT:    (C) 2013 by the GRASS Development Team
 *
 *               This program is free software under the GNU General
 *               Public License (>=v2).  Read the file COPYING that
 *               comes with GRASS for details.
 *
 **************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <grass/gis.h>
#include <grass/raster.h>
#include <grass/glocale.h>
#include <grass/dbmi.h>
#include <grass/vector.h>


/* ************************************************************************** */

static void sample(char *input, char *rast, char *column, char *output) {

	struct Cell_head window;
	struct Map_info In, Out;
	int fdrast;
	DCELL value;
	G_get_window(&window);
	int line;
	int type;
	struct field_info *Fi;
	dbDriver *Driver;
	char buf[2000];
	dbString sql;
	DCELL *dcell_buf;

	/* Open input */
	Vect_set_open_level(2);
	Vect_open_old2(&In, input, "", "1");
	fdrast = Rast_open_old(rast, "");

	/* Open output */
	Vect_open_new(&Out, output, 0);
	Vect_hist_copy(&In, &Out);
	Vect_hist_command(&Out);

	/* Create table */
	Fi = Vect_default_field_info(&Out, 1, NULL, GV_1TABLE);
	Vect_map_add_dblink(&Out, Fi->number, Fi->name, Fi->table, Fi->key,
			Fi->database, Fi->driver);
	Driver = db_start_driver_open_database(Fi->driver,
			Vect_subst_var(Fi->database, &Out));
	sprintf(buf, "create table %s ( cat integer, rast_val double precision)",
			Fi->table);
	db_init_string(&sql);
	db_set_string(&sql, buf);
	db_execute_immediate(Driver, &sql);
	db_create_index2(Driver, Fi->table, Fi->key);
	db_grant_on_table(Driver, Fi->table, DB_PRIV_SELECT, DB_GROUP | DB_PUBLIC);

	/* Sample the raster map with vector points */
	struct line_pnts *Points = Vect_new_line_struct();
	struct line_cats *Cats = Vect_new_cats_struct();
	int nlines = Vect_get_num_lines(&In);
	int count = 0;

	dcell_buf = Rast_allocate_buf(DCELL_TYPE);

	db_begin_transaction(Driver);

	for (line = 1; line <= nlines; line++) {
		type = Vect_read_line(&In, Points, Cats, line);

		if (!(type & GV_POINT))
		    continue;

		if(G_point_in_region(Points->x[0], Points->y[0]) == 0)
			continue;

		if (Rast_is_d_null_value(&value))
		    continue;

		int row = Rast_northing_to_row(Points->y[0], &window);
		int col = Rast_easting_to_col(Points->x[0], &window);

		Rast_get_d_row(fdrast, dcell_buf, row);
		value = dcell_buf[col];

		/* Write value into the vector table */
		count++;
		Vect_reset_cats(Cats);
		Vect_cat_set(Cats, 1, count);
		Vect_write_line(&Out, GV_POINT, Points, Cats);

		sprintf(buf, "INSERT INTO %s VALUES ( %d, %e ); ", Fi->table, count,
				(double)value);
		db_set_string(&sql, buf);
		db_execute_immediate(Driver, &sql);
	}

    db_commit_transaction(Driver);
	db_close_database_shutdown_driver(Driver);

	Rast_close(fdrast);
	Vect_close(&In);
	Vect_build(&Out);
	Vect_close(&Out);

	exit(EXIT_SUCCESS);
}

/* ************************************************************************** */

int main(int argc, char **argv) {
	struct GModule *module;
	struct {
		struct Option *input, *output, *rast, *column;
	} parm;

	G_gisinit(argv[0]);

	module = G_define_module();
	G_add_keyword(_("vector"));
	G_add_keyword(_("sampling"));
	G_add_keyword(_("raster"));
	module->description = _("Samples a raster map at vector point locations.");

	parm.input = G_define_standard_option(G_OPT_V_INPUT);
	parm.input->label = _("Name of input vector point map");

	parm.column = G_define_standard_option(G_OPT_DB_COLUMN);
	parm.column->required = YES;
	parm.column->description =
			_("Name of attribute column to use for comparison");

	parm.output = G_define_standard_option(G_OPT_V_OUTPUT);
	parm.output->description = _("Name for output vector map");

	parm.rast = G_define_standard_option(G_OPT_R_INPUT);
	parm.rast->key = "raster";
	parm.rast->description = _("Name of raster map to be sampled");

	if (G_parser(argc, argv))
		exit(EXIT_FAILURE);

	sample(parm.input->answer, parm.rast->answer, parm.column->answer,
			parm.output->answer);

	return 0;
}
