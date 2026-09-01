Scratch directory for the figure scripts.

The symlinks here point at the HMToL pipeline's precomputed `.npz` intermediates and its
`assets/` (the Natural Earth geojson and the OWID HDI table), so
`figs/hmtol_web_figs.py` can repoint `hmtol_lib.SW` here without writing into
`AGP/Report/hmtol/pipeline`. Nothing in this directory is part of the site.

Recreate with:

    P="$HOME/Library/CloudStorage/OneDrive-UniversityofCalifornia,SanDiegoHealth/AGP/Report/hmtol/pipeline"
    for f in country_var_full core_prev core_prev_rare country_between disease_birdman \
             succession hdi full_pub full_pub_clean; do ln -sf "$P/$f.npz" .; done
    ln -sf "$P/pruned.nwk" . ; ln -sfn "$P/assets" .
    ln -sf "$P/assets/ne110.geojson" . ; ln -sf "$P/assets/hdi_owid.csv" .
