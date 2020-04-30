# tiny class to generate maps based on a template

from PIL import Image
import errno
import os

class MapFiller():
    def __init__(self):
        self.dict_pixels = dict()


    def fill_map(self, path_to_new_file='result_image.png'):

        """
        :param path_to_new_file: Path to finished image

        Return: True when the image was created. False when an error occurred

        The fill_map() method creates a new map image. Pixels for painting are 
        taken from the dictionary obtained by the load_target_pixels() method
        """

        if self.dict_pixels:
            try:
                img = Image.open(self.path_to_map)
            except FileNotFoundError:
                print(str.format("  * Error: Map file '{}' does not exist",
                    self.path_to_map))

                return False

            except PermissionError:
                print(str.format("  * Error: Map file '{}'. Permission denied",
                    self.path_to_map))

                return False

            else:
                pixels = img.load()
                width, height = img.size

            for key in self.dict_pixels.keys():
                values = self.dict_pixels.get(key)
                color = values['color']
                for position in values['pixels']:
                    try:
                        pixels[position[0], position[1]] = (color[0], 
                                                            color[1], 
                                                            color[2], 255)
                    except TypeError:
                        print("  * Warrnig: TypeError")

            img.save(path_to_new_file)
            return True
        else:
            print("  * Error: The image was not created,"
                + " because the dictionary of regions is empty")

            return False


    def load_target_pixels(self, id_region, rgb_array, metafile):

        """
        :param id_region: ID region or unique region name
        :param rgb_array: RGB array. Intensities for each color in the range 
            from 0 to 255
        :param metafile: Path to the metafile

        Return: True if the file was read successfully. 
            False if the file is ignored 

        The load_target_pixels() method tries to load a metafile and set 
        the color to be used for filling the region. You must use 
        the set_color() method to change the fill color after load
        """

        pixels = self.read_meta_file(metafile)
        
        if pixels:
            self.dict_pixels.update({id_region: {
                'color': rgb_array, 
                'pixels': pixels}})
            return True

        else:
            print(str.format("  * Ignored: {}", metafile))
            return False


    def map(self, path_to_map):

        """ 
        :param path_to_map: A file that contains region masks

        Return: True if file exists. False when an error occurred

        The map() method specifies the file with region masks to use
        """

        if os.access(path_to_map, os.F_OK) == True:
            self.path_to_map = path_to_map
            return True
        else:
            print(str.format("  * Error: Map file '{}' does not exist", 
                path_to_map))
            return False


    def read_meta_file(self, metafile):

        """
        :param metafile: Path to the metafile

        Return: An array of pixels that match that region. 
            False when problems occur
        """

        metadata = []

        try:
            with open(metafile) as file:
                raw = file.read()
                raw_lines = raw.split("\n")
                meta_info = raw_lines[1].replace("\t","").split("=")

                if "META_VERSION" == meta_info[0]:
                    if meta_info[1] == "1.0":
                        metadata = self._extract_data(raw_lines)
                    else:
                        print(str.format("  * Error: '{}' unknown format version",
                            metafile))

                        return False

                else:
                    print(str.format("  * Error: The metafile '{}' is damaged,"
                        + " can't read it", metafile))

                    return False

            return metadata
        
        except FileNotFoundError:
            print(str.format("  * Error: The metafile '{}' does not exist", 
                metafile))

            return False

        except PermissionError:
            print(str.format("  * Error: The metafile '{}'. Permission denied",
                metafile))

            return False


    def set_color(self, id_region, rgb_array):

        """
        The set_color() method specifies the new color of the region
        """

        try:
            tmp = self.dict_pixels.get(id_region)
            self.dict_pixels.update({id_region: {'color': rgb_array, 
            'pixels': tmp['pixels']}})

        except TypeError:
            print(str.format("  * Error: Unable to update region '{}' because"
                + " it was not loaded", id_region))

            return False

        else:
            return True


    def write_meta_file(self, hex_color, id_region, id_country=None, folder='',
        discription=None):

        """
        :param discription: Description, region name or comment on the file. 
            None by default
        :param folder: Path to the folder where the file will be saved
        :param id_country: Not a required field. None by default
        :param id_region: Required field, id region or unique region name to use 
            as the file name
        :param hex_color: Unique hex color of the region

        Return: True if the file was created. 
            False if the file could not be created

        The write_meta_file() creates a file with pixel's coordinates, which 
        relate to a specific region on the map
        """

        meta_region = []
        hex_color = hex_color.lower()

        header = str.format("[ HEADER:\n\tMETA_VERSION=1.0\n" 
            + "\tcountry={id_country};\n\tregion={id_region};\n"
            + "\tdiscription='{discription}';\n]\n", id_country=id_country,
                                                     id_region=id_region,
                                                     discription=discription)

        try:
            with Image.open(self.path_to_map) as img:
                pixels = img.load()
                width, height = img.size

                for x in range(width):
                    for y in range(height):
                        r, g, b, a = pixels[x, y]
                        pix_hex_color = str.format("{:02x}{:02x}{:02x}", r,g,b)
                        if pix_hex_color == hex_color:
                            meta_region.append([x, y])

        except FileNotFoundError:
            print(str.format("  * Error: Map file '{}' does not exist", 
                self.path_to_map))

            return False

        except PermissionError:
            print(str.format("  * Error: Map file '{}'. Permission denied",
                self.path_to_map))

            return False

        if folder:
            try: 
                os.makedirs(folder)
                path_to_meta_file = str.format("{}/{}.mf", folder, id_region)
            except OSError as exception: 
                if exception.errno != errno.EEXIST:
                    raise
                else:
                    path_to_meta_file = str.format("{}/{}.mf", folder, id_region)
        else:
            path_to_meta_file = str.format("{}.mf", folder, id_region)
        
        try:
            with open(path_to_meta_file, "w") as file:
                file.write(header)
                file.write("DATA:\n")
                
                for row in meta_region:
                    file.write(str.format("{}x{} ", row[0], row[1]))

        except PermissionError:
            print(str.format("  * Error: Can't create metafile '{}'."
                + " Permission denied", path_to_meta_file))

            return False


    def _extract_data(self, raw_lines):

        """
        :param raw_lines: Data received from the file

        Return: Array of coordinates of the region's pixels to change.
            False if the 'Data' block is not found
        """

        for row, lines in enumerate(raw_lines):
            if "DATA:" in lines:
                pixels = raw_lines[row+1].split(" ")
                pixels_array = []
                
                for pixel in pixels:
                    if len(pixel) >= 3:
                        x, y = pixel.split("x")
                        pixels_array.append([int(x), int(y)])

                return pixels_array
            
        print("  * Error: Can't find the data," 
            + " the file structure may be damaged")

        return False
