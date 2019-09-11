# -*- coding: utf-8 -*-
from modules import compressionTools
from tempfile import _get_candidate_names, _get_default_tempdir
from sqlite3 import Binary
from os.path import isfile, basename, splitext, join


def file_add(self, fName, componentID, datasheet = False, compression = compressionTools.COMPRESSION_FMT.LZMA):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    if isfile(fName):
        filename = basename(fName)
        try:
            with open(fName, 'rb') as fIn:
                _blob = compressionTools.compressData(fIn.read(), compression)
                file_id = self.query(
                    "INSERT INTO Files VALUES (?, ?, ?, ?);",
                    (
                        None,
                        componentID,
                        filename,
                        datasheet
                    )
                )
                file_data = self.query(
                    "INSERT INTO Files_blob VALUES (?, ?, ?);",
                    (
                        file_id[0],
                        Binary(_blob),
                        int(compression)
                    )
                )

                self.conn.commit()
                return True

        except Exception as e:
            self.log.error("There was an error adding the file to database: {}".format(e))
            self.conn.rollback()
            return False

    else:
        self.log.error("The file {} does not exists".format(pdf))
        return False


def file_del(self, fileID):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    try:
        self.query(
            "DELETE FROM Files WHERE ID = ?;",
            (
                fileID,
            )
        )
        self.conn.commit()
        return True

    except Exception as e:
        self.log.error("There was an error deleting then file from database")
        self.conn.rollback()
        return False


def file_export(self, fileID, fName = None):
    if self.templates:
        self.log.warning(
            "This function is not compatible with templates" +
            " databases"
        )
        return False

    exists = self.query("SELECT Filename FROM Files WHERE ID = ?", (fileID,))
    if len(exists) > 0:
        try:
            blob_data = self.query("SELECT Filedata, Filecompression FROM Files_blob WHERE File_id = ?", (fileID,))
            if not fName:
                tempName = next(_get_candidate_names())
                tempFolder = _get_default_tempdir()

                # La extensión la sacamos del nombre de fichero en la BBDD
                filename, extension = splitext(exists[0][0])
                fName = join(
                    tempFolder,
                    tempName +
                    extension
                )

            with open(fName, 'wb') as fOut:
                fOut.write(compressionTools.decompressData(blob_data[0][0], blob_data[0][1]))

            return fName
        except Exception as e:
            self.log.error("There was an error writing file temporary file: {}".format(e))
            return False
    else:
      return False