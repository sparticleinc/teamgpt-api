import json
from datetime import datetime, timedelta
from typing import Union

import pytz
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends, Security
from fastapi_auth0 import Auth0User
from starlette.responses import RedirectResponse

from teamgpt.enums import StripeModel
from teamgpt.models import StripeWebhookLog, StripePayments, StripeProducts, Organization, User, UserOrganization, \
    SystemConfig
from teamgpt.schemata import StripeProductsOut, OrgPaymentPlanOut, PaymentPlanInt
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
    obj = await StripePayments.filter(organization_id=organization_id, deleted_at__isnull=True).prefetch_related(
        'stripe_products').order_by('-created_at').first()
    stripe.api_key = STRIPE_API_KEY
    if obj is None:
        return None
    # 取出obj到新的对象,并且增加sub_info
    req_obj = dict(obj)
    req_obj['product_info'] = {}
    product = await StripeProducts.filter(api_id=obj.api_id).first()

    if obj.mode == StripeModel.SUBSCRIPTION:
        sub_info = stripe.Subscription.retrieve(
            obj.sub_id,
        )

        req_obj['sub_info'] = sub_info
    if obj.mode == StripeModel.PAYMENT:
        pay_info = stripe.PaymentIntent.retrieve(
            obj.payment_id
        )
        if pay_info is not None:
            req_obj['sub_info'] = {
                'current_period_start': pay_info.created,
                'current_period_end': pay_info.created + 86400 * (product.month * 30),
            }
        if obj.type == 'checkout.session.completed':
            req_obj['sub_info']['status'] = 'success'
        elif obj.type == 'canceled':
            req_obj['sub_info']['status'] = 'canceled'
    if product.product is not None:
        product_info = stripe.Product.retrieve(
            product.product,
        )
        req_obj['product_info'] = product_info
    if product is not None:
        req_obj['product_info']['order'] = product.order

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
                                      type__in=['payment_intent.succeeded',
                                                'checkout.session.completed']).prefetch_related(
        'stripe_products').order_by('-created_at').first()
    if obj is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    stripe.api_key = STRIPE_API_KEY
    if obj.mode == StripeModel.SUBSCRIPTION:
        sub_info = stripe.Subscription.delete(
            obj.sub_id,
        )
        return sub_info
    if obj.mode == StripeModel.PAYMENT:
        await StripePayments.filter(id=obj.id).update(type='canceled')
        return None


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
        # 查询付费计划
        product = await StripeProducts.filter(api_id=api_id, deleted_at__isnull=True).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': api_id,
                    'quantity': 1,
                },
            ],
            mode=product.mode.value,
            success_url=origin,
            cancel_url=origin,
            metadata={
                'organization_id': organization_id,
                'origin': origin,
                'api_id': api_id,
                'mode': product.mode.value,
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

        event_type = event.type

        # 获取事件的元数据
        metadata = event.data.object.get("metadata")

        # 根据事件类型进行不同的处理，同时将 organization_id 与事件进行关联
        if event_type == "payment_intent.succeeded":
            # 支付成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"支付成功：{payment_id} invoice:{invoice}")

        elif event_type == "payment_intent.payment_failed":
            # 支付失败
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"支付失败：{payment_id} invoice:{invoice}")
        elif event_type == "charge.succeeded":
            # 付款成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"已付款：{payment_id} invoice:{invoice}")
        elif event_type == "charge.refunded":
            # 退款成功
            payment_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"已退款：{payment_id} invoice:{invoice}")
        elif event_type == "customer.subscription.created":
            # 订阅已创建
            subscription_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"订阅已创建：{subscription_id} invoice:{invoice}")
        elif event_type == "customer.subscription.updated":
            # 订阅已更新
            subscription_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"订阅已更新：{subscription_id} invoice:{invoice}")
        elif event_type == "customer.subscription.deleted":
            # 订阅已取消
            subscription_id = event.data.object.id
            sub_id = event.data.object.get("id")
            print(f"订阅已取消：{subscription_id} sub_id:{sub_id}")
            await StripePayments.filter(
                sub_id=sub_id,
            ).update(type='customer.subscription.deleted')

        elif event_type == "invoice.payment_succeeded":
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
                     sub_id=lines.data[0]['subscription'])
        elif event_type == "checkout.session.completed":
            # Checkout 支付已完成
            checkout_id = event.data.object.id
            organization_id = metadata.get("organization_id")
            api_id = metadata.get("api_id")
            mode = metadata.get("mode")
            invoice = event.data.object.get("invoice")
            payment_id = event.data.object.get("payment_intent")
            stripe_products_obj = await StripeProducts.filter(api_id=api_id).first()
            await StripePayments.create(
                type='checkout.session.completed',
                stripe_products_id=stripe_products_obj.id,
                invoice=invoice,
                payment_id=payment_id,
                api_id=api_id,
                mode=mode,
                organization_id=organization_id,
                customer_details=json.dumps(event.data.object.get("customer_details")),
            )
            print(f"Checkout 支付已完成：{checkout_id} [组织 ID：{organization_id}] invoice:{invoice}")
        elif event_type == "account.updated":
            # Stripe 账户已更新
            account_id = event.data.object.id
            invoice = event.data.object.get("invoice")
            print(f"Stripe 账户已更新：{account_id} invoice:{invoice}")
        else:
            # 其他事件
            print(f"其他事件类型：{event_type}")
        return {"message": "success"}
    except Exception as e:
        # 其他异常错误
        print(f"其他异常错误：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# 判断组织属性,是否在试用期,是否过期,和付费计划
async def org_payment_plan(org_obj: Organization) -> OrgPaymentPlanOut:
    out = OrgPaymentPlanOut()
    if org_obj.super is True:
        out.is_join = True
        out.is_super = True
        out.is_send_msg = True
        return out
    # 查询组织是否有付费计划
    obj = await StripePayments.filter(organization_id=org_obj.id, deleted_at__isnull=True,
                                      type__in=['payment_intent.succeeded',
                                                'checkout.session.completed', 'canceled']).prefetch_related(
        'stripe_products').order_by('-created_at').first()
    org_user_number = await UserOrganization.filter(organization_id=org_obj.id, deleted_at__isnull=True).count()
    if obj is None:
        obj = await StripePayments.filter(organization_id=org_obj.id, deleted_at__isnull=True,
                                          type='customer.subscription.deleted').prefetch_related(
            'stripe_products').order_by('-created_at').first()
        if obj is not None:
            products_obj = await StripeProducts.filter(id=obj.stripe_products_id).first()
            days = products_obj.month * 30
            created_at_utc = obj.created_at.astimezone(pytz.utc)
            out.expiration_time = str(created_at_utc + timedelta(days=days))
            # 比较时间戳
            if created_at_utc + timedelta(days=days) < datetime.now(pytz.timezone('UTC')):
                obj = None
    if obj:
        # 查看已经有多少人了,使用了是什么套餐
        products_obj = await StripeProducts.filter(id=obj.stripe_products_id).first()
        days = products_obj.month * 30
        out.expiration_time = str(obj.created_at.astimezone(pytz.utc) + timedelta(days=days))
        out.is_send_msg = True
        if products_obj is None:
            return out
        out.is_plan = True
        out.plan_max_number = products_obj.max_number
        out.plan_remaining_number = products_obj.max_number - org_user_number
        out.sys_token = products_obj.sys_token
        if out.plan_remaining_number > 0:
            out.is_join = True
            return out
        return out
    # 查询是否有退订的,还没过期的套餐

    # 查询组织是否在试用期
    out.is_try = True
    created_at_utc = org_obj.created_at.astimezone(pytz.utc)
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    out.expiration_time = str(created_at_utc + timedelta(days=3))
    if created_at_utc + timedelta(days=3) < now_utc:
        out.is_try = False
    else:
        out.is_try = True
        out.is_send_msg = True
        out.try_day = abs((now_utc - (created_at_utc + timedelta(days=3))).days)
        if org_user_number < 3:
            out.is_join = True
    return out


@router.post("/payment",
             )
async def payment_plan(org_input: Union[PaymentPlanInt] = None, user: Auth0User = Security(auth.get_user)):
    if org_input is None:
        user_info = await User.get_or_none(user_id=user.id, deleted_at__isnull=True)
        if user_info is None:
            return None
        if user_info.current_organization is None or user_info.current_organization is '':
            return None
        org_obj = await Organization.get_or_none(id=user_info.current_organization, deleted_at__isnull=True)
    else:
        org_obj = await Organization.get_or_none(id=org_input.organization_id, deleted_at__isnull=True)
    info = await org_payment_plan(org_obj)
    # 定义一个dict接收info的值
    info_dict = info.dict()
    # 增加一个变量
    info_dict['pricing_map'] = await SystemConfig.filter(name='products').values()
    return info_dict
