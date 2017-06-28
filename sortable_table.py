from itertools import cycle

import pygame as pg

import prepare, tools
from labels import Label, LOADED_FONTS, _parse_color


SORTABLE_TABLE_DEFAULTS = {
    "bg_color": "gray90",
    "line_color": "gray40",
    "line_weight": 1,
    "light_field_bg": "gray90",
    "dark_field_bg": "gray 80",
    "field_text_font": None,
    "field_text_size": 16,
    "field_text_color": "gray5",
    "header_text_font": None,
    "header_text_size": 24,
    "header_text_color": "gray5",
    "field_height": 30,
    "header_height": 48}


class FieldHeader(object):
    """
    Create a header for each field in the SortableTable. Clicking on
    the header sorts the table according to that field. Subsequent
    clicks toggle the sorting order.
    """
    def __init__(self, name, topleft, width, height, fill_color,
                      line_color, line_weight, header_text_font,
                      header_text_size, header_text_color):
        """"
        ARGS

        name: the name of the field the header controls
        topleft: the topleft screen position of the table
        width: the width of the field the header controls
        height: the height of the header's rect
        fill_color: color to fill the header's rect with
        line_color: the line color of the SortableTable
        """
        self.image = pg.Surface((width, height))
        self.image.fill(fill_color)
        center = (width//2), height // 2
        self.field_name = name
        label = Label(name, {"center": center}, font_path=header_text_font,
                           font_size=header_text_size, text_color=header_text_color)
        label.draw(self.image)
        pg.draw.rect(self.image, line_color, ((0, 0), (width, height)), line_weight)
        self.rect = self.image.get_rect(topleft=topleft)
        self.direction = -1
        self.selected = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class TableRow(object):
    """Object to represent a single row of data in the SortableTable."""
    def __init__(self, data_dict, field_widths, field_height, field_text_font,
                      field_text_size, field_text_color):
        """
        ARGS

        data_dict: an OrderedDict of field_name: value pairs
        field_widths: list of the widths for each field (ordered to match the order of keys in data_dict)
        field_height: the height of a field's rect
        text_color: color that field values should be rendered in
        """
        self.data = data_dict
        left, top = 0, 0
        total_width = sum(field_widths)
        self.image = pg.Surface((total_width, field_height)).convert_alpha()
        self.image.fill((0,0,0,0))
        right = left
        for width, field_name in zip(field_widths, data_dict):
            right += width
            value = data_dict[field_name]
            label = Label("{}".format(value),
                              {"midright": (right - 3, top + (field_height // 2))},
                              text_color=field_text_color, font_size=field_text_size,
                              font_path=field_text_font)
            label.draw(self.image)
        self.rect = self.image.get_rect()


class RowSlot(object):
    """
    Object to represent a row in the SortableTable. Used to set
    the position of TableRows after sorting.
    """
    def __init__(self, num, topleft, row_width, field_height):
        """
        ARGS

        num: the number of the RowSlot (0 is the top row in the table)
        topleft: the positon of the row on the SortableTable's image
        row_width: total width of rows in the table
        field_height: height of each field's rect
        """
        self.num = num
        self.topleft = topleft
        self.size = row_width, field_height


class SortableTable(tools._KwargMixin):
    """
    A scrollable, sortable table consisting of rows of fields which can
    be sorted according to the values in a field. Sorting can be toggled
    between ascending and descending.
    """
    def __init__(self, onscreen_rect, data_dicts, field_widths, **kwargs):
        """
        ARGS

        onscreen_rect: the rect that the table will occupy on the screen
        data_dicts: a list of OrderedDict objects of field_name: value pairs
        field_widths: a list of the widths for each field ordered to match the
                           order of keys in each data_dict
        field_height: height of each field's rect
        header_height: height of each FieldHeader's rect
        """
        self.process_kwargs("SortableTable", SORTABLE_TABLE_DEFAULTS, kwargs)
        self.bg_color = _parse_color(self.bg_color)
        self.line_color = _parse_color(self.line_color)
        self.light_field_bg = _parse_color(self.light_field_bg)
        self.dark_field_bg = _parse_color(self.dark_field_bg)
        self.field_text_color = _parse_color(self.field_text_color)
        self.header_text_color = _parse_color(self.header_text_color)

        self.rect = onscreen_rect
        row_width = sum(field_widths)
        num_rows = len(data_dicts)
        self.table_height = (num_rows * self.field_height) + self.header_height
        self.make_row_slots(num_rows, row_width)
        self.make_rows(data_dicts, field_widths)
        self.make_headers(data_dicts[0], field_widths)
        self.view_rect = pg.Rect((0, 0), self.rect.size)
        self.base_image = pg.Surface((row_width, self.table_height))
        self.base_image.fill(self.bg_color)
        self.table_rect = self.base_image.get_rect()
        colors = cycle([self.light_field_bg, self.dark_field_bg])
        for slot in self.slots:
            color = next(colors)
            pg.draw.rect(self.base_image, color,
                             (slot.topleft, slot.size), self.line_weight)
            pg.draw.line(self.base_image, self.line_color,
                             (self.table_rect.left, slot.topleft[1]),
                             (self.table_rect.right, slot.topleft[1]),
                             self.line_weight)
        for h in self.headers:
            pg.draw.line(self.base_image, self.line_color,
                             (h.rect.right - self.rect.left, self.table_rect.top),
                             (h.rect.right - self.rect.left, self.table_rect.bottom),
                             self.line_weight)
        self.sort(list(data_dicts[0].keys())[0], 1)

    def make_row_slots(self, num_rows, row_width):
        self.slots = []
        left, top = 0, self.header_height
        for num in range(num_rows):
            self.slots.append(RowSlot(num, (left, top), row_width, self.field_height))
            top += self.field_height

    def make_rows(self, data_dicts, field_widths):
        self.rows = []
        for d in data_dicts:
            self.rows.append(
                    TableRow(d, field_widths, self.field_height,
                                  self.field_text_font, self.field_text_size,
                                  self.field_text_color))

    def make_headers(self, data_dict, field_widths):
        self.headers = []
        left, top = self.rect.topleft
        for name, width in zip(data_dict, field_widths):
            header = FieldHeader(name, (left, top), width, self.header_height,
                                          self.bg_color, self.line_color, self.line_weight,
                                          self.header_text_font, self.header_text_size,
                                          self.header_text_color)
            self.headers.append(header)
            left += width

    def scroll(self, direction, amount=16):
        self.view_rect.top -= direction * amount
        if self.view_rect.top < 0:
            self.view_rect.top = 0
        if self.view_rect.bottom > self.table_rect.bottom:
            self.view_rect.bottom = self.table_rect.bottom

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                for header in self.headers:
                    if header.rect.collidepoint(event.pos):
                        if header.selected:
                            header.direction *= -1
                        else:
                            for h in self.headers:
                                h.selected = False
                            header.selected = True
                            header.direction = -1
                        self.sort(header.field_name, header.direction)
            elif event.button == 4:
                self.scroll(1)
            elif event.button == 5:
                self.scroll(-1)
        elif event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                self.scroll(1)
            elif event.key == pg.K_DOWN:
                self.scroll(-1)            

    def sort(self, field_name, direction):
        descending = True if direction == -1 else False
        self.image = self.base_image.copy()
        ranked = sorted(self.rows, key=lambda x: x.data[field_name], reverse=descending)
        for row, slot in zip(ranked, self.slots):
            row.rect.topleft = slot.topleft
            self.image.blit(row.image, row.rect)
        self.view_rect.top = 0

    def draw(self, surface):
        surface.blit(self.image.subsurface(self.view_rect), self.rect)
        for h in self.headers:
            h.draw(surface)
        pg.draw.rect(surface, self.line_color, self.rect, self.line_weight)
