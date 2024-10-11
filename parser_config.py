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
       Xay dung 1 file moi config file duoc parse.

        """
        self.config = config
        self.fname = fname
        self.status = 0
        self.error = ''

    # thiet ke cac ham tim loi nguoi dung nhap vao:

    def type_error(self, key, want, got):
        """
        Tra ve status va thong diep error khi type -> loi trong config file.

          """
        self.status = 1
        self.error = f'Key \'{key}\' expected {want}, found {got}'


    def unknown_key_error(self, key):
        """
       Tra ve status va thong diep error khi key unknown trong config file.

        """
        self.status = 1
        self.error = f'Unknown key \'{key}\' in {self.fname}'


    def missing_key_error(self, key, dict_name):
        """
       Thieu key -> bat loi.

        """
        self.status = 1
        self.error = f'Missing key \'{key}\' in {dict_name}'

    def unknown_value_error(self, key, value):
        """
        Value error trong key
        """
        self.status = 1
        self.error = f'Unknown value \'{value}\' for key \'{key}\''

    def neg_float_error(self, key, value):
        """
         So thuc am -> Bat loi
        """
        self.status = 1
        self.error = (f'Key \'{key}\' must have a non-negative value. Found '
            f' value \'{value}\'')


    def non_pos_int_error(self, key, value):
        """
        So nguyen khong am --> bat loi
        """
        self.status = 1
        self.error = (f'Key \'{key}\' must have a positive value. Found value '
            f'\'{value}\'')

    def min_max_error(self, min_key, min_value, max_key, max_value):
        """
        Min < max --> bat loi
        """
        self.status = 1
        self.error = (f'Key \'{min_key}\':\'{min_value}\' must have a value '
            f'less than or equal to key \'{max_key}\':\'{max_value}\'')

    def parse_int(self, key, value):
        """
        Gia tri int trong value cua 1 so key su dung ham isinstance;
        """
        if not (isinstance(value, int)):
            self.type_error(key, 'int', str(type(value)))
            return
        if value < 1:
            self.non_pos_int_error(key, value)



    def parse_float(self, key, value):
        """
      Check float trong key --> value.

        """
        if not (isinstance(value, float)):
            self.type_error(key, 'float', str(type(value)))
            return
        if value < 0:
            self.neg_float_error(key, value)


    def parse_bool(self, key, value):
        """
        Check bool

        """
        if not (isinstance(value, bool)):
            self.type_error(key, 'boolean', str(type(value)))


    def parse_box_orientation(self, orientation):
        """
        Check orientation is valid

        """
        if orientation not in self.box_orientations:
            self.unknown_value_error('orientation', orientation)

    def parse_box_type(self, box_type):
        """
        Gia tri box_type
        """
        if box_type not in self.box_types:
            self.unknown_value_error('type', box_type)


    def parse_string(self, key, value):
        """
       parse doi voi key == type va orientation
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
        group

        """
        self.parse_float(key, value)

    def parse_group(self, group):
        """
        Check group trong dict -> tra ve error + message
        :param group:
        :return:
        """
        if isinstance(group, dict):
            # Check for missing keys:
            for key in self.group_keys:
                if key not in group:
                    self.missing_key_error(key, group)
                    break

            for (key, value) in group.items():
                if key in self.group_keys:
                    self.parse_group_key(key, value)
                else:
                    self.unknown_key_error(key)
                    break

            if group['x_min'] > group['x_max']:
                self.min_max_error('x_min', group['x_min'], 'x_max', group['x_max'])
            if group['y_min'] > group['y_max']:
                self.min_max_error('y_min', group['y_min'], 'y_max', group['y_max'])

        else:
            self.type_error('group', 'dict', str(type(group)))

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

    def parse_groups(self, groups):
        """
        Groups -> group -> parse group
        :param groups:
        :return:
        """

        if isinstance(groups, list):
            for group in groups:
                self.parse_group(group)
        else:
            self.type_error('groups', 'list', str(type(groups)))


    def parse_boxes(self, boxes):
        """
      boxes -> check lists -> box

        """
        if isinstance(boxes, list):
            for box in boxes:
                self.parse_box(box)
        else:
            self.type_error('boxes', 'list', str(type(boxes)))

    def parse_config_key(self, key, value):
        """
       Parse key + value trong config dict

        """
        if key == 'boxes':
            self.parse_boxes(value)
        else:
            self.parse_float(key, value)

    def parse(self):
        """
        Check dict -> parse

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
    Check du lieu la 1 cap -> Phat hien

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