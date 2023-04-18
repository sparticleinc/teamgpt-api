import json
import uuid

import stripe
from fastapi import APIRouter, Depends, Security, HTTPException, Request
from fastapi_auth0 import Auth0User
from fastapi_pagination import Page
from starlette.responses import RedirectResponse
from starlette.status import HTTP_204_NO_CONTENT

from teamgpt.models import GPTKey, User, Organization, SysGPTKey, StripeWebhookLog
from teamgpt.parameters import ListAPIParams, tortoise_paginate
from teamgpt.schemata import GPTKeyOut, GPTKeyIn, SysGPTKeyIn, SysGPTKeyOut, StripeCheckoutIn
from teamgpt.settings import (auth, STRIPE_API_KEY, DOMAIN)

router = APIRouter(prefix='/api/v1/stripe', tags=['Stripe'])


@router.get(
    '/create-checkout',
    # dependencies=[Depends(auth.implicit_scheme)],
)
async def get_my_organizations(
        lookup_key: str,
        organization_id: str
):
    try:
        stripe.api_key = STRIPE_API_KEY
        prices = stripe.Price.list(
            lookup_keys=[lookup_key],
            expand=['data.product']
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=DOMAIN + '/success.html',
            cancel_url=DOMAIN + '/cancel.html',
        )
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except Exception as e:
        print(e)
        return "Server error", 500


@router.post('/webhook')
async def webhook(request: Request):
    payload = await request.body()
    event = json.loads(payload)
    await StripeWebhookLog.create(
        type=event['type'],
        data=json.dumps(event['data']),
    )
