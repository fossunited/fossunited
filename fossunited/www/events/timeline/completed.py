from .index import get_context as base_get_context


def get_context(context):
    base_get_context(context, page_type="completed")
