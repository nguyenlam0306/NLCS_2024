class Parser:

    config_keys = ['page_width', 'page_height', 'bubble_width', 'bubble_height',
                   'qr_x', 'qr_y', 'x_error', 'y_error', 'boxes']

    box_keys = ['name', 'type', 'orientation', 'multiple_responses', 'x', 'y',
                'rows', 'columns', 'groups']

    group_keys = ['x_min', 'x_max', 'y_min', 'y_max']

    box_types = ['letter', 'number']

    box_orientations = ['left-to-right', 'top-to-bottom']

