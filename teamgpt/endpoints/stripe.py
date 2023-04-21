import json

import stripe
from fastapi import APIRouter, Request, HTTPException, Depends, Security
from fastapi_auth0 import Auth0User
from starlette.responses import RedirectResponse

from teamgpt.models import StripeWebhookLog, StripePayments, StripeProducts, Organization, User
from teamgpt.schemata import StripeProductsOut
from teamgpt.settings import (STRIPE_API_KEY, DOMAIN, auth)

router = APIRouter(prefix='/api/v1/stripe', tags=['Stripe'])


# 查询StripeProducts
@router.get(
    '/products',
    dependencies=[Depends(auth.implicit_scheme)],
    response_model=list[StripeProductsOut],
)
async def get_products(user: Auth0User = Security(auth.get_user)):
    user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    if user_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    obj_list = await StripeProducts.filter(deleted_at__isnull=True).all()
    return obj_list


# 查询组织付费计划
@router.get(
    '/pay/{organization_id}',
    dependencies=[Depends(auth.implicit_scheme)],
)
async def get_pay(organization_id: str, user: Auth0User = Security(auth.get_user)):
    # user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
    org_obj = await Organization.filter(id=organization_id, deleted_at__isnull=True).get_or_none()
    if org_obj is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    # if org_obj.creator_id != user_info.id:
    #     raise HTTPException(status_code=403, detail="You are not the creator of the organization")
    obj = await StripePayments.filter(organization_id=organization_id, deleted_at__isnull=True,
                                      type='payment_intent.succeeded').prefetch_related(
        'stripe_products').get_or_none()
    stripe.api_key = STRIPE_API_KEY
    if obj is None:
        return None
    sub_info = stripe.Subscription.retrieve(
        obj.sub_id,
    )
    product_info = stripe.Product.retrieve(
        sub_info['plan']['product'],
    )
    # 取出obj到新的对象,并且增加sub_info
    req_obj = dict(obj)
    req_obj['sub_info'] = sub_info
    req_obj['product_info'] = product_info
    if req_obj is None:
        return None
    return req_obj


# 更改组织退订计划
@router.post(
    '/cancel/{organization_id}',
    dependencies=[Depends(auth.implicit_scheme)],
)
async def cancel_pay(organization_id: str, user: Auth0User = Security(auth.get_user)):
    org_obj = await Organization.filter(id=organization_id, deleted_at__isnull=True).get_or_none()
    if org_obj is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    obj = await StripePayments.filter(organization_id=organization_id, deleted_at__isnull=True,
                                      type='payment_intent.succeeded').prefetch_related(
        'stripe_products').get_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    stripe.api_key = STRIPE_API_KEY
    sub_info = stripe.Subscription.delete(
        obj.sub_id,
    )
    print(sub_info, 'sddd')


@router.get(
    '/create-checkout',
    # dependencies=[Depends(auth.implicit_scheme)],
)
async def get_my_organizations(
        api_id: str,
        organization_id: str,
        origin: str,
):
    try:
        if origin == '':
            origin = DOMAIN
        stripe.api_key = STRIPE_API_KEY
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': api_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=origin,
            cancel_url=origin,
            metadata={
                'organization_id': organization_id,
                'origin': origin
            }
        )
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/webhook')
async def webhook(request: Request):
    # 获取请求体
    payload = await request.body()
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        await StripeWebhookLog.create(
            type=event['type'],
            data=json.dumps(event['data']),
        )

        eventType = event.type

        # 获取事件的元数据
        metadata = event.data.object.get("metadata")

        # 根据事件类型进行不同的处理，同时将 organization_id 与事件进行关联
        if eventType == "payment_intent.succeeded":
            # 支付成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"支付成功：{payment_id} invoice:{invoice}")

        elif eventType == "payment_intent.payment_failed":
            # 支付失败
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"支付失败：{payment_id} invoice:{invoice}")
        elif eventType == "charge.succeeded":
            # 付款成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"已付款：{payment_id} invoice:{invoice}")
        elif eventType == "charge.refunded":
            # 退款成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"已退款：{payment_id} invoice:{invoice}")
        elif eventType == "customer.subscription.created":
            # 订阅已创建
            subscription_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"订阅已创建：{subscription_id} invoice:{invoice}")
        elif eventType == "customer.subscription.updated":
            # 订阅已更新
            subscription_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"订阅已更新：{subscription_id} invoice:{invoice}")
        elif eventType == "customer.subscription.deleted":
            # 订阅已取消
            subscription_id = event.data.object.id
            sub_id = event.data.object.get("id")
            print(f"订阅已取消：{subscription_id} sub_id:{sub_id}")
            await StripePayments.filter(
                sub_id=sub_id,
            ).update(type='customer.subscription.deleted')

        elif eventType == "invoice.payment_succeeded":
            # 发票已支付
            invoice_id = event.data.object.id
            invoice = event.data.object.get("id")
            lines = event.data.object.get("lines")
            print(f"发票已支付：{invoice_id} invoice:{invoice}")
            product_obj = await StripeProducts.filter(
                api_id=lines.data[0]['plan']['id']).first()
            await StripePayments.filter(
                invoice=invoice,
            ).update(stripe_products_id=product_obj.id, type='payment_intent.succeeded',
                     sub_id=lines.data[0]['subscription'],
                     api_id=lines.data[0]['plan']['id'])
        elif eventType == "checkout.session.completed":
            # Checkout 支付已完成
            checkout_id = event.data.object.id
            organization_id = metadata.get("organization_id")
            invoice = event.data.object.get("invoice")
            await StripePayments.create(
                type='checkout.session.completed',
                invoice=invoice,
                organization_id=organization_id,
                customer_details=json.dumps(event.data.object.get("customer_details")),
            )
            print(f"Checkout 支付已完成：{checkout_id} [组织 ID：{organization_id}] invoice:{invoice}")
        elif eventType == "account.updated":
            # Stripe 账户已更新
            account_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"Stripe 账户已更新：{account_id} invoice:{invoice}")
        else:
            # 其他事件
            print(f"其他事件类型：{eventType}")
        return {"message": "success"}
    except Exception as e:
        # 其他异常错误
        print(f"其他异常错误：{e}")
        raise HTTPException(status_code=500, detail=str(e))
