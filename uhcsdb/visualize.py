import os
import sys
import glob
import h5py
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, contains_eager

from bokeh.layouts import row, widgetbox
from bokeh.plotting import curdoc, figure
from bokeh.models import Select, ColumnDataSource, HoverTool, OpenURL, TapTool

from models import Base, User, Collection, Sample, Micrograph

# only show micrographs with these class labels
unique_labels = np.array(
    ['spheroidite', 'spheroidite+widmanstatten', 'martensite', 'network',
     'pearlite', 'pearlite+spheroidite', 'pearlite+widmanstatten']
)

# set marker colors -- keep consistent with paper
colornames = ["blue", "cerulean", "red",
              "dusty purple", "saffron", "dandelion", "green"]
rgbmap = {label: sns.xkcd_rgb[c]
          for label, c in zip(unique_labels, colornames)}

# custom markup for plot marker tooltips with thumbnails and metadata
hover = HoverTool(
    tooltips="""
    <div>
      <div height="100px" width="130px">
        <img
          src="@thumb" alt="@thumb"
          style="float: center; margin: 0px 15px 15px 0px; width: 100px; height: 100px"
          border="2"
        ></img>
      </div>
      <div>
        <span style="font-size: 17px; font-weight: bold; color: #990000;">Class</span>
        <span style="font-size: 15px;">@mclass</span>
      </div>
      <div>
        <span style="font-size: 15px; color: #990000;">Temperature</span>
        <span style="font-size: 10px;">@temperature C</span>
      </div>
      <div>
        <span style="font-size: 15px; color: #990000;">Time</span>
        <span style="font-size: 10px;">@time minutes</span>
      </div>
      <div>
        <span style="font-size: 15px; color: #990000;">Mag</span>
        <span style="font-size: 10px;">@mag microns/px</span>
      </div>
    </div>
"""
)

def load_tsne(featuresfile, keys, perplexity=40):
    """load t-SNE map points from hdf5 into a numpy array.

    ordered by primary keys
    """
    
    with h5py.File(featuresfile, 'r') as f:        
        g = f['perplexity-{}'.format(perplexity)]
        X = [g[key][...] for key in keys]

    return np.array(X)


def load_embedding(featuresfile, keys, method='PCA'):
    """ load reduced dimensionality map points from hdf5 into numpy array.

    ordered by primary keys.
    """
    
    with h5py.File(featuresfile, 'r') as f:        
        g = f[method]
        X = [g[key][...] for key in keys]

    return np.array(X)


def connect_db(dbpath):
    """return a sqlalchemy database connection."""
    engine = create_engine('sqlite:///' + dbpath)
    Base.metadata.bind = engine
    dbSession = sessionmaker(bind=engine)
    return dbSession()


def assign_color(colorvar):
    """masked colormap for quantitative metadata.

    pass bokeh hex color strings for marker colors.
    """
    m = np.ma.array(colorvar, mask=(colorvar == -9999))

    reds = mpl.cm.Reds
    reds.set_bad('black', 0.3)
    c = reds(mpl.colors.Normalize(vmin=np.min(m), vmax=np.max(m))(m))

    col = ["#%02x%02x%02x" % (r, g, b)
           for r, g, b, a in (255*c).astype(int)]

    alpha = 1 - 0.7*m.mask
    return col, alpha

def assign_scale(scalevar):
    """masked markersize for quantitative metadata."""
    m = np.ma.array(scalevar, mask=(scalevar == -9999))
    sc = 30*((m-np.min(m)) / np.max(m)) + 10
    sc[m.mask] = 5

    alpha = 1 - 0.7*m.mask
    return sc, alpha


def update_map_points(attr, old, new):
    """update plot data in response to bokeh widget form data."""
    print(type(attr))
    print(old)
    print(new)
    global current_manifold
    global current_representation
    
    if (representation.value != current_representation
        or manifold.value != current_manifold):
        # update marker locations
        
        if manifold.value == 't-SNE':
            hfile = os.path.join('static', 'tsne', representation.value)
            X = load_tsne(hfile, keys=df['id'].astype(str), perplexity=40)
        else:
            hfile = os.path.join('static', 'embed', representation.value)
            X = load_embedding(hfile, keys=df['id'].astype(str), method=manifold.value)
            
        source.data['x'] = X[:,0]
        source.data['y'] = X[:,1]
        current_representation = representation.value
        current_manifold = manifold.value

        
def update_marker_color(attr, old, new):
    """update marker color metadata."""
    
    if colorctl.value == 'primary microconstituent':
        col = [rgbmap[cls] for cls in df['mstructure_class']]
        alpha = 0.8 * np.ones(df.index.size)
    else:
        if colorctl.value == 'log(scale)':
            col, alpha = assign_color(np.log(np.array(source.data['mag'])))
        else:
            col, alpha = assign_color(df[colorctl.value].values)

    source.data['c'] = col
    source.data['alpha'] = alpha

    
def update_marker_size(attr, old, new):
    """update marker size metadata."""

    # set sane defaults
    if size.value == 'None':
        sz = 10*np.ones(df.index.size)
        alpha = 0.8 * np.ones(df.index.size)
    else:
        sz, alpha = assign_scale(df[size.value].values)
        
    source.data['size'] = sz
    source.data['alpha'] = alpha
    

# load metadata for all micrographs into pandas dataframe
db = connect_db('microstructures.sqlite')
q = (db.query(Micrograph)
     .outerjoin(Micrograph.sample)
     .options(contains_eager(Micrograph.sample))
     .filter(Micrograph.mstructure_class.in_(unique_labels)
     )
)
df = pd.read_sql_query(q.statement, con=db.connection())

# Both Micrograph and Sample tables have an 'id' field...
# loading the whole dataset into a pandas df yields two 'id' columns
# drop the id field that results from Micrograph.sample.id
df = df.T.groupby(level=0).last().T
df = df.replace(np.nan, -9999) # bokeh (because json) can't deal with NaN values

# convert times to minutes, in place
df.ix[df.anneal_time_unit=='H', 'anneal_time'] *= 60

# set default form data to draw the default plot
current_representation = 'vgg16_block5_conv3-vlad-32.h5'                        
representations = list(map(os.path.basename, glob.glob('static/tsne/*.h5')))
representation = Select(title='Representation', value=current_representation, options=representations)
representation.on_change('value', update_map_points)

current_manifold = 't-SNE'
manifold_methods = ['PCA', 't-SNE', 'MDS', 'LLE', 'Isomap', 'SpectralEmbedding']
manifold = Select(title='Manifold method', value=current_manifold, options=manifold_methods)
manifold.on_change('value', update_map_points)

size = Select(title='Marker size', value='None', options=['None'] + ['anneal_temperature', 'anneal_time'])
size.on_change('value', update_marker_size)

colorctl = Select(title='Marker color', value='primary microconstituent', options=['primary microconstituent'] + ['anneal_temperature', 'anneal_time', 'log(scale)'])
colorctl.on_change('value', update_marker_color)

hfile = os.path.join('static', 'tsne', representation.value)
x = load_tsne(hfile, keys=df['id'].astype(str), perplexity=40)

thumb = ['static/thumbs/micrograph{}.png'.format(key) for key in df['id']]

source =  ColumnDataSource(
    data=dict(
        key=df['id'].values,
        x=x[:,0],
        y=x[:,1],
        thumb=thumb,
        temperature=df['anneal_temperature'].values,
        time=df['anneal_time'].values,
        mclass=df['mstructure_class'].values,
        mag=df['micron_bar'].values/df['micron_bar_px'].values, # TODO: convert units!
        size=10*np.ones(df.index.size),
        c = [rgbmap[cls] for cls in df['mstructure_class']],
        alpha=0.8*np.ones(df.index.size),
    )
)


p = figure(plot_height=800, plot_width=800, title='UHCS microstructure explorer',
           tools=['crosshair', 'pan', 'reset', 'save', 'wheel_zoom', 'tap', hover])
circles = p.circle(x='x', y='y', source=source, size='size', color='c', alpha='alpha', line_color="black", line_alpha=0.3)
p.toolbar.active_scroll = 'auto'

# url_for_entry = "visual_query/@key"
url_for_entry = "micrograph/@key"
taptool = p.select(type=TapTool)
taptool.callback = OpenURL(url=url_for_entry)

controls = widgetbox([representation, manifold, colorctl, size], width=256)
curdoc().add_root( row(controls, p) )
curdoc().title = "UHCSDB: a microstructure explorer"
