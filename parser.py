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
