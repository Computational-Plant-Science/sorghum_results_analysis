# run pipeline
python3 /opt/code/pipeline.py -i $INPUT -o $OUTPUT --n_plane $N_PLANE --slicing_ratio $SLICING_RATIO --adjustment $ADJUSTMENT

# copy nested output files to working directory
find . -type f -name "*.xlsx" -exec cp {} $WORKDIR \;