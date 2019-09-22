# -*- coding: utf-8 -*-
from modules import imageResizeWX, compressionTools
from wx import BITMAP_TYPE_PNG, BITMAP_TYPE_JPEG, BITMAP_TYPE_BMP
from sqlite3 import Binary


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
        image = imageResizeWX.imageResizeWX(
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

    query = ""
    if category:
        query = """
            INSERT INTO
              [Images](
                [Category_id],
                [Image],
                [Imagecompression]
              )
            VALUES (?, ?, ?);
        """
    else:
        query = """
            INSERT INTO
              [Images](
                [Component_id],
                [Image],
                [Imagecompression]
              )
            VALUES (?, ?, ?);
        """
    try:
        self.query(
            query,
            (
                parent,
                Binary(image_data),
                compression
            )
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
        self.query(
            """DELETE FROM [Images] WHERE [ID] = ?;""",
            (
                imageID,
            )
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting the image: {}".format(e))
        self.conn.rollback()
        return False
