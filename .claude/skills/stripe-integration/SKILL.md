---
name: stripe-integration
description: Implement Stripe payments correctly with webhooks, subscriptions, customer management
---

# Stripe Integration

Implements Stripe payment flows, webhooks, subscriptions following best practices.

## When to Use
- Adding payment processing
- Setting up subscriptions
- Implementing webhooks
- Customer portal integration
- Payment testing

## Components

### 1. Payment Flows
- Checkout sessions
- Payment intents
- Setup intents (saved cards)
- Multi-step flows
- SCA/3DS handling

### 2. Webhooks (CRITICAL)
Must handle:
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`

### 3. Subscriptions
- Products and prices
- Lifecycle management
- Proration
- Trials
- Metered billing

### 4. Customers
- Create records
- Update payment methods
- Billing portal
- Invoice history

## Implementation Pattern

1. **Test Mode First**: Use test keys
2. **Idempotency**: Keys for mutations
3. **Webhook Validation**: Verify signatures
4. **Error Handling**: Graceful degradation
5. **Testing**: Use Stripe CLI

## Security Checklist
- [ ] API keys in env variables
- [ ] Webhook signatures validated
- [ ] Amount calculations server-side
- [ ] No client-side price manipulation
- [ ] HTTPS only

## Webhook Setup
```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

## Best Practices
- Webhooks = source of truth (not client events)
- Store Stripe customer ID with user record
- Use metadata for database linking
- Implement retries
- Test all lifecycle events

## Example Usage
```
"Use Stripe integration skill to add monthly/annual subscriptions.
Need webhook handling and customer portal."
```
