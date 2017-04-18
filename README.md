# [UHCSDB dataset explorer](http://uhcsdb.materials.cmu.edu)
A dynamic microstructure exploration application built on Flask and Bokeh.

Run flask app uhcsdb/uhcsdb.py in parallel with bokeh app uhcsdb/visualize.py

The Ultrahigh Carbon Steel (UHCS) microstructure dataset is available on [materialsdata.nist.gov](https://hdl.handle.net/11256/940) ([https://hdl.handle.net/11256/940)](https://hdl.handle.net/11256/940).
Please cite use of the UHCS microstructure data as:
```TeX
@misc{uhcsdata,
  title={Ultrahigh Carbon Steel Micrographs},
    author = {Hecht, Matthew D. and DeCost, Brian L. and Francis, Toby and Holm, Elizabeth A. and Picard, Yoosuf N. and Webler, Bryan A.},
      howpublished={\url{https://hdl.handle.net/11256/940}}
      }
```	

The UHCS dataset will be documented by an [IMMI](https://immijournal.springeropen.com/) manuscript (submitted 14 April 2017).
For work that builds on these data visualization tools, please cite our forthcoming IMMI manuscript:
```TeX
@article{uhcsimmi,
  title={UHCSDB (Ultrahigh Carbon Steel micrograph DataBase): tools for exploring large heterogeneous microstructure datasets},
  author = {DeCost, Brian L. and Hecht, Matthew D. and Francis, Toby  and Picard, Yoosuf N. and Webler, Bryan A. and Holm, Elizabeth A.},
  year={submitted for review},
  journal={IMMI}
}
```	


Store microstructure metadata in uhcsdb/microstructures.sqlite
Store image files under uhcsdb/static/micrographs.
Store image representations in HDF5 under uhcsdb/static/representations.
Store reduced-dimensionality representations in HDF5 under uhcsdb/static/embed.
