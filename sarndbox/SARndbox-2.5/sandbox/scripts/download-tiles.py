import logging
from landez import MBTilesBuilder

logging.basicConfig(level=logging.DEBUG)

mb = MBTilesBuilder(
    tiles_url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    cache=False,
    filepath="esri-highres.mbtiles",
)
mb.add_coverage(bbox=(-7.818751263994194, 29.932874506926854, 72.01133072878456, 64.56842453507622),
                zoomlevels=[0, 1, 2, 3, 4, 5, 6, 7, 8])
mb.run()
