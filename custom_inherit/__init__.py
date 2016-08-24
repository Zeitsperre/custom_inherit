from __future__ import absolute_import
from types import FunctionType, MethodType
from abc import ABCMeta
from .metaclass_base import DocInheritorBase
from .style_store import *
from .decorator_base import DocInheritDecorator
from .style_store import __all__ as all_styles

try:
    basestring
except NameError:
    basestring = str  # Python 2 -> 3 alias


__all__ = ["DocInheritMeta", "doc_inherit", "store", "add_style", "remove_style"]
__version__ = "2.0.0"


class Store(dict):
    """ A dictionary that stores the styles available for the doc-inheritance metaclass and decorator,
       respectively."""
    def __str__(self):
        out_str = "The available stored styles are: "
        styles = "\n".join("\t- " + style for style in sorted(self.keys()))
        return "\n".join((out_str, styles))

    def __setitem__(self, style_name, style_func):
        """ Make available a new function for merging a 'parent' and 'child' docstring.

            Parameters
            ----------
            style_name : Any
                The identifier of the style being logged
            style_func: Callable[[Optional[str], Optional[str]], Optional[str]]
                The style function that merges two docstrings into a single docstring."""
        try:
            style_func("", "")
        except TypeError:
            raise TypeError("The style store only stores functions of the form:\
             \n\tfunc(Optional[str], Optional[str]) -> Optional[str]")
        super(Store, self).__setitem__(style_name, style_func)

    def __getitem__(self, item):
        try:
            return super(Store, self).__getitem__(item)
        except KeyError:
            try:
                item("", "")
            except TypeError:
                raise TypeError("Either a valid style name or style-function must be specified")
            return item

store = Store()
for style_kind in style_store.__all__:
    _style = getattr(style_store, style_kind)
    if isinstance(_style, (FunctionType, MethodType)):
        store[style_kind] = _style


def add_style(style_name, style_func):
    """ Make available a new function for merging a 'parent' and 'child' docstring.

        Parameters
        ----------
        style_name : Any
            The identifier of the style being logged
        style_func: Callable[[Optional[str], Optional[str]], Optional[str]]
            The style function that merges two docstrings into a single docstring."""
    store[style_name] = style_func


def remove_style(style):
    """ Remove the specified style from the style store.

        Parameters
        ----------
        style: Any
            The valid inheritance-scheme style ID to be removed."""
    if style in store:
        store.pop(style)


def DocInheritMeta(style="parent", abstract_base_class=False):
    """ Returns the DocInheritor metaclass of the specified style.

        Parameters
        ----------
        style: Union[Any, Callable[[str, str], str]], optional (default: "parent")
            A valid inheritance-scheme style ID or function that merges two docstrings.

        abstract_base_class: bool, optional(default: False)
            If True, the returned metaclass inherits from abc.ABCMeta.

            Thus a class that derives from DocInheritMeta(style="numpy", abstract_base_class=True)
            will be an abstract base class, whose derived classes will inherit docstrings
            using the numpy-style inheritance scheme.


        Returns
        -------
        custom_inherit.DocInheritorBase"""

    merge_func = store[style]
    metaclass = DocInheritorBase
    metaclass.class_doc_inherit = staticmethod(merge_func)
    metaclass.attr_doc_inherit = staticmethod(merge_func)

    return metaclass if not abstract_base_class else type("abc" + metaclass.__name__, (ABCMeta, metaclass), {})


def doc_inherit(parent, style="parent"):
    """ Returns a function/method decorator that, given `parent`, updates the docstring of the decorated
        function/method based on the specified style and `parent`.

        Parameters
        ----------
        prnt_doc : Union[str, Any]
            The docstring, or object of which the docstring is utilized as the
            parent docstring during the docstring merge.

        style : Union[Any, Callable[[str, str], str]], optional (default: "parent")
            A valid inheritance-scheme style ID or function that merges two docstrings.

        Returns
        -------
        custom_inherit.DocInheritDecorator"""
    merge_func = store[style]
    decorator = DocInheritDecorator
    decorator.doc_merger = staticmethod(merge_func)
    return decorator(parent)
