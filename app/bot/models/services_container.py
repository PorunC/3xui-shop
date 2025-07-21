from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bot.services import (
        NotificationService,
        PlanService,
        ProductService,
        ReferralService,
        SubscriptionService,
        PaymentStatsService,
        InviteStatsService,
    )

from dataclasses import dataclass


@dataclass
class ServicesContainer:
    plan: PlanService
    product: ProductService
    notification: NotificationService
    referral: ReferralService
    subscription: SubscriptionService
    payment_stats: PaymentStatsService
    invite_stats: InviteStatsService
