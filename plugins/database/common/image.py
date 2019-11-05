# -*- coding: utf-8 -*-
from modules import imageResize, compressionTools
from wx import BITMAP_TYPE_PNG, BITMAP_TYPE_JPEG, BITMAP_TYPE_BMP


def image_add(self, image, size, parent, category, format=BITMAP_TYPE_PNG,
              quality=None, compression=compressionTools.COMPRESSION_FMT.LZMA):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates"
            " databases"
        )
        return False

    self.log.debug("Adding image:")
    self.log.debug("   format: {}".format(format))
    self.log.debug("   quality: {}".format(quality))
    self.log.debug("   compression: {}".format(compression))
    try:
        color = (-1, -1, -1)
        if format == BITMAP_TYPE_JPEG or format == BITMAP_TYPE_BMP:
            self.log.debug("Image has not transparent support")
            color = (255, 255, 255)
        image = imageResize.imageResize(
            image,
            nWidth=size[0],
            nHeight=size[1],
            out_format=format,
            compression=quality,
            color=color
        )
        image_data = compressionTools.compressData(image.getvalue(), compression)

    except IOError:
        self.log.error("Cannot open file '%s'." % image)

    try:
        if category:
            self._insert(
                "Images",
                items=[
                    "Category_id",
                    "Image",
                    "Imagecompression"
                ],
                values=[
                    parent,
                    self.file_to_blob(image_data),
                    int(compression)
                ]
            )
        else:
            self._insert(
                "Images",
                items=[
                    "Component_id",
                    "Image",
                    "Imagecompression"
                ],
                values=[
                    parent,
                    self.file_to_blob(image_data),
                    compression
                ]
            )

        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error adding the image: {}".format(e))
        self.conn.rollback()
        return False


def image_del(self, imageID):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    try:
        self._delete(
            "Images",
            where=[
                {'key': 'ID', 'value': imageID}
            ]
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the image: {}".format(e))
        self.conn.rollback()
        return False
