from typing import Optional, Type, Union, TypeVar, Generic

from fastapi import Query
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.tortoise import paginate as _tortoise_paginate
from tortoise.models import Model
from tortoise.query_utils import Prefetch
from tortoise.queryset import QuerySet
from fastapi_pagination.default import Page as BasePage, Params as BaseParams

IGNORE_PARAMS = ['params', 'page', 'size', 'order_by']

T = TypeVar('T')


class Params(BaseParams):
    size: int = Query(50, ge=1, le=1_0000, description='Page size')


class Page(BasePage[T], Generic[T]):
    __params_type__ = Params


class ListAPIParams(Params):
    order_by: Optional[str] = Query(Query(
        None,
        description='Sort order, allowing order by multiple columns, separated by `,`, use `-` for reverse order.',
    ))


async def tortoise_paginate(
    query: Union[QuerySet, Type[Model]],
    params: Optional[ListAPIParams] = None,
    prefetch_related: Union[bool, list[Union[str, Prefetch]]] = False,
) -> AbstractPage:
    if not isinstance(query, QuerySet):
        query = query.all()
    if params and params.order_by:
        order_by = params.order_by.replace(' ', '').split(',')
        query = query.order_by(*order_by)
    return await _tortoise_paginate(
        query=query,
        params=params,
        prefetch_related=prefetch_related,
    )
