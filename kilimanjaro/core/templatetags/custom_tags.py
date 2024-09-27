"""This file contains some custom template tags, 
    Which are also used in django admin customized html files"""

from typing import Any

from django import template

register = template.Library()


@register.filter(name="convert_string_to_list")
def convert_string_to_list(errors_list: Any) -> list:
    # Takes string wrapped list and returns list

    errors_list = errors_list.args[0]
    if isinstance(errors_list, str):  # A single string
        errors_list = [errors_list]  # Converts string into list
    return errors_list


# Replacing a string with another string
@register.simple_tag
def replace_with(
    self, replace_from: str, replace_to: str
):  # 'replace_from' value should be string wrapted list
    field_name = self
    for replace_word in list(eval(replace_from)):
        field_name = field_name.replace(replace_word, " ")

    return field_name.upper()
