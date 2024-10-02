class Parser:

    config_keys = ['page_width', 'page_height', 'bubble_width', 'bubble_height',
                   'qr_x', 'qr_y', 'x_error', 'y_error', 'boxes']

    box_keys = ['name', 'type', 'orientation', 'multiple_responses', 'x', 'y',
                'rows', 'columns', 'groups']

    group_keys = ['x_min', 'x_max', 'y_min', 'y_max']

    box_types = ['letter', 'number']

    box_orientations = ['left-to-right', 'top-to-bottom']

    def __init__(self, config, fname):
        """
        Constructor for a new config file parser.

        Args:
            config (dict): A dictionary containing the config file values for
                this test box.
            fname (str): The name of the config file being parsed.

        Returns:
            Parser: A newly created parser.

        """
        self.config = config
        self.fname = fname
        self.status = 0
        self.error = ''
# thiet ke cac ham tim loi nguoi dung nhap vao:

    def type_error(self, key, want, got):
        """
        Sets the status and error message for a type error in the config file.

        Args:
            key (str): The name of the key with a type error.
            want (str): The expected type for that key.
            got (str): The received type for that key.

        """
        self.status = 1
        self.error = f'Key \'{key}\' expected {want}, found {got}'


    def unknown_key_error(self, key):
        """
        Sets the status and error message for an unknown key in the config file.

        Args:
            key (str): The name of the unknown key.

        """
        self.status = 1
        self.error = f'Unknown key \'{key}\' in {self.fname}'


    def missing_key_error(self, key, dict_name):
        """
        Sets the status and error message for a missing key in the config file.

        Args:
            key (str): The name of the missing key.
            dict_name (str): The location of the missing key.

        """
        self.status = 1
        self.error = f'Missing key \'{key}\' in {dict_name}'

    def unknown_value_error(self, key, value):
        """
        Sets the status and error message for a key with an unknown value in the
        config file.

        Args:
            key (str): The name of the key with a value error.
            value (str): The unknown value for the given key.

        """
        self.status = 1
        self.error = f'Unknown value \'{value}\' for key \'{key}\''

    def neg_float_error(self, key, value):
        """
        Sets the status and error message for a key with a negative float value.

        Args:
            key (str): The name of the key with a negative value error.
            value (float): The negative float value.

        """
        self.status = 1
        self.error = (f'Key \'{key}\' must have a non-negative value. Found '
            f' value \'{value}\'')


    def non_pos_int_error(self, key, value):
        """
        Sets the status and error message for a key with a non-positive int
        value.

        Args:
            key (str): The name of the key with a non positive value error.
            value (int): The non positive int value.

        """
        self.status = 1
        self.error = (f'Key \'{key}\' must have a positive value. Found value '
            f'\'{value}\'')

    def min_max_error(self, min_key, min_value, max_key, max_value):
        """
        Sets the status and error message for a min value greater than a max
        value.

        Args:
            min_key (str): The name of the min key.
            min_value (float): The value of the min key.
            max_key (str): The name of the max key.
            max_value (float): The value of the max key.

        """
        self.status = 1
        self.error = (f'Key \'{min_key}\':\'{min_value}\' must have a value '
            f'less than or equal to key \'{max_key}\':\'{max_value}\'')

    def parse_int(self, key, value):
        """
        Checks if a value is of type int. If not, sets error status and message.

        Args:
            key (str): The key associated with the value being checked.
            value (int): The value being checked.

        """
        if not (isinstance(value, int)):
            self.type_error(key, 'int', str(type(value)))
            return
        if value < 1:
            self.non_pos_int_error(key, value)



    def parse_float(self, key, value):
        """
        Checks if a value is of type float. If not, sets error status and
        message.

        Args:
            key (str): The key associated with the value being checked.
            value (float): The value being checked.

        """
        if not (isinstance(value, float)):
            self.type_error(key, 'float', str(type(value)))
            return
        if value < 0:
            self.neg_float_error(key, value)


    def parse_bool(self, key, value):
        """
        Checks if a value is of type boolean. If not, sets error status and
        message.

        Args:
            key (str): The key associated with the value being checked.
            value (boolean): The value being checked.

        """
        if not (isinstance(value, bool)):
            self.type_error(key, 'boolean', str(type(value)))


    def parse_box_orientation(self, orientation):
        """
        Checks if the orientation is valid. If not, sets error status and
        message.

        Args:
            orientation (str): The orientation of bubbles in a test box.

        """
        if orientation not in self.box_orientations:
            self.unknown_value_error('orientation', orientation)

    def parse_box_type(self, box_type):
        """
        Checks if the box type is valid. If not, sets error status and message.

        Args:
            box_type (str): The type of bubbles in a test box.

        """
        if box_type not in self.box_types:
            self.unknown_value_error('type', box_type)


    def parse_string(self, key, value):
        """
        Checks if a value is of type string. If the value is of type string,
        parses its value. If not, sets error status and message.

        Args:
            key (str): The key associated with the value being checked.
            value (str): The value being checked.

        """
        if isinstance(value, str):
            if key == 'type':
                self.parse_box_type(value)
            elif key == 'orientation':
                self.parse_box_orientation(value)
        else:
            self.type_error(key, 'str', str(type(value)))


    def parse_group_key(self, key, value):
        """
        Checks if the group value is valid. All group values should be of type
        float.

        Args:
            key (str): The key associated with the value being checked.
            value (float): The value being checked.

        """
        self.parse_float(key, value)


    def parse_box_key(self, key, value):
        """
        Parses key/value pairs in a box dict.

        Args:
            key (str): The key associated with the value being checked.
            value (?): The value being checked.

        """
        if key == 'name' or key == 'type' or key == 'orientation':
            self.parse_string(key, value)
        elif key == 'x' or key == 'y':
            self.parse_float(key, value)
        elif key == 'rows' or key == 'columns':
            self.parse_int(key, value)
        elif key == 'multiple_responses':
            self.parse_bool(key, value)
        elif key == 'groups':
            self.parse_groups(value)

    def parse_box(self, box):
        """
        Checks if a box is of type dict. If it is, parses each key/value pair,
        checking for missing and unknown keys. If not, sets error status and
        message.

        Args:
            box (dict): The box dict being checked.

        """
        # Check that box is dict.
        if isinstance(box, dict):
            # Check for missing keys.
            for key in self.box_keys:
                if key not in box:
                    self.missing_key_error(key, 'box')
                    break

            # Parse each key/value and check for unknown keys.
            for (key, value) in box.items():
                if key in self.box_keys:
                    self.parse_box_key(key, value)
                else:
                    self.unknown_key_error(key)
                    break
        else:
            self.type_error('box', 'dict', str(type(box)))

    def parse_boxes(self, boxes):
        """
        Checks if boxes is of type list. If it is, parses each member of the
        list. If not, sets error status and message.

        Args:
            boxes (list): The list of box dicts.

        """
        if isinstance(boxes, list):
            for box in boxes:
                self.parse_box(box)
        else:
            self.type_error('boxes', 'list', str(type(boxes)))

    def parse_config_key(self, key, value):
        """
        Parses key/value pairs in a config dict.

        Args:
            key (str): The key associated with the value being checked.
            value (?): The value being checked.

        """
        if key == 'boxes':
            self.parse_boxes(value)
        else:
            self.parse_float(key, value)

    def parse(self):
        """
        Checks if config is of type dict. If it is, parses each key/value pair.
        If not, sets error status and message.

        Returns:
            status (int): 0 if no errors detected, 1 otherwise.
            error (str): Error message if error detected.

        """
        # Check that config is dict.
        if isinstance(self.config, dict):
            # Check for missing keys.
            for key in self.config_keys:
                if key not in self.config:
                    self.missing_key_error(key, 'config')
                    break

            # Parse each key/value and check for missing keys.
            for (key, value) in self.config.items():
                if key in self.config_keys:
                    self.parse_config_key(key, value)
                else:
                    self.unknown_key_error(key)
                    break
        else:
            self.type_error('config', 'dict', str(type(self.config)))

        # Returns status and error message after parsing entire config dict.
        return self.status, self.error

def duplicate_key_check(ordered_pairs):
    """
    Raise value error if duplicate keys detected in config file.

    Args:
        ordered_pairs (list): A key/value pair in the config file.

    Returns:
        d (dict): A dictionary containing the key/value pair.

    """
    d = {}

    for (key, value) in ordered_pairs:
        if key in d:
            raise ValueError('duplicate key: %r' % key)
        else:
            d[key] = value

    return d