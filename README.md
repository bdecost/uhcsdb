# [UHCSDB dataset explorer](http://uhcsdb.materials.cmu.edu)
A dynamic microstructure exploration application built on Flask and Bokeh.

Run flask app uhcsdb/uhcsdb.py in parallel with bokeh app uhcsdb/visualize.py

The Ultrahigh Carbon Steel (UHCS) microstructure dataset is available on [materialsdata.nist.gov](https://hdl.handle.net/11256/940) ([https://hdl.handle.net/11256/940)](https://hdl.handle.net/11256/940).
Please cite use of the UHCS microstructure data as:
```TeX
@misc{uhcsdata,
  title={Ultrahigh Carbon Steel Micrographs},
  author={Hecht, Matthew D. and DeCost, Brian L. and Francis, Toby and Holm, Elizabeth A. and Picard, Yoosuf N. and Webler, Bryan A.},
  howpublished={\url{https://hdl.handle.net/11256/940}}
}
```	

The UHCS dataset is be documented by a data descriptor published in IMMI (doi: [10.1007/s40192-017-0097-0](https://dx.doi.org/10.1007/s40192-017-0097-0)).
You can read our preprint version [here (pdf)](https://holmgroup.github.io/publications/uhcs-data.pdf].
For work that builds on these data visualization tools, please cite our forthcoming IMMI manuscript:
```TeX
@article{uhcsimmi,
  title={UHCSDB (Ultrahigh Carbon Steel micrograph DataBase): tools for exploring large heterogeneous microstructure datasets},
  author={DeCost, Brian L. and Hecht, Matthew D. and Francis, Toby  and Picard, Yoosuf N. and Webler, Bryan A. and Holm, Elizabeth A.},
  year={2017},
  journal={Accepted for publication in IMMI},
  doi={10.1007/s40192-017-0097-0}
}
```	

## Check out the data

```sh
git clone https://github.com/bdecost/uhcsdb
cd uhcsdb
```

Store microstructure metadata in uhcsdb/microstructures.sqlite
```sh
# get data from NIST for this project
# http://hdl.handle.net/11256/940
NIST_DATASET=11256/940
NIST_DATASET_URL=https://materialsdata.nist.gov/dspace/xmlui/bitstream/handle/${NIST_DATASET}

DATADIR=uhcsdata

echo "download data files into DATADIR=${DATADIR}"

# download metadata
curl ${NIST_DATASET_URL}/microstructures.sqlite -o ${DATADIR}/microstructures.sqlite
```

Store image files under uhcsdb/static/micrographs.

Store image representations in HDF5 under uhcsdb/static/representations.

Store reduced-dimensionality representations in HDF5 under uhcsdb/static/embed.
```sh
for archivefile in micrographs.zip representations.zip embed.zip; do
    curl ${NIST_DATASET_URL}/${archivefile} -o ${DATADIR}/${archivefile}
    unzip ${DATADIR}/${archivefile} -d ${DATADIR}
done
```

Link data files into web app /static

```sh
curl ${NIST_DATASET_URL}/setup.sh -o ${DATADIR}/setup.sh
bash setup.sh
```


