#!/usr/bin/python3
# -*- coding: utf-8 -*-

# example of using the class

import sqlite3
import math
from mapfiller import MapFiller


def set_palette_level(value, max_value):
    return math.floor((value/max_value)*10)


def main():
    # example of creating a palette
    color_palette = dict()

    color_palette.update({0: [175, 175, 175]})
    color_palette.update({1: [238, 246, 236]})
    color_palette.update({2: [214, 236, 210]})
    color_palette.update({3: [183, 221, 176]})
    color_palette.update({4: [153, 209, 143]})
    color_palette.update({5: [123, 200, 108]})
    color_palette.update({6: [97, 189, 79]})
    color_palette.update({7: [90, 172, 68]})
    color_palette.update({8: [81, 152, 57]})
    color_palette.update({9: [73, 133, 46]})
    color_palette.update({10: [63, 111, 33]})

    mf = MapFiller()
    bmap = mf.map("./demo/example-map.png")

    if bmap:
    
        db = sqlite3.connect("./demo/db.sqlite")
        cursor = db.cursor()
    
        # example of creating a metafile from the database
        cursor.execute("SELECT hex_color, id_iso_3166_2, default_name_region "
            + "FROM tbls_regions_info")

        result = cursor.fetchall()

        for row in result:
            mf.write_meta_file(row[0], row[1], folder="./demo/mf", discription=row[2]) 

        # example creating a map using data from a database
        cursor.execute("SELECT `trs`.`id_iso_3166_2`, `trs`.`population`,"
            + "`tri`.`path_metafile` "
            + "FROM tbl_regions_stat trs "
            + "LEFT JOIN tbls_regions_info tri "
            + "   ON `tri`.`id_iso_3166_2` = `trs`.`id_iso_3166_2` "
            + "WHERE `trs`.`date_stat` = '2019-01-01'")
        
        result = cursor.fetchall()
        max_value = max(result, key=lambda item:item[1])[1]

        for row in result:
            mf.load_target_pixels(row[0], color_palette.get(
                set_palette_level(row[1], max_value)), row[2]) 

        mf.fill_map('result.png')

        db.close()


if __name__ == '__main__':
    main()
