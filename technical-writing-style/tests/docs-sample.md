# Configuring Notifications For Shared Projects

In today's fast-paced digital world, teams need to stay informed. This section explains how to configure notifications for shared projects.

Notifications are sent by the system when a task changes — for example, when a task is assigned, completed, or commented on; you can also be notified when a due date is close.

## Prerequisites

The user must have the Admin role. Please note that notifications are not available on the Free plan.

## Turning On Notifications

1. Click on Settings > Notifications.
2. Check the box labeled "Email me when a task is assigned to me"
3. Select the frequency (e.g. Instant, Hourly, Daily).
4. Changes are saved automatically in near real time.

Notifications will soon support SMS delivery.

## Delivery Details

The notifier service polls the events table every 500 ms and batches messages in the worker pool. If delivery fails, the system may not always behave as expected.

Our powerful, intuitive notification engine always ensures that you never miss an update. 15 notification types are supported; the most important are listed below:

- assignment of a task
- Task completed
- When someone comments

Use the SLA settings to escalate overdue tasks. For API access, call `POST /notifications/subscribe` with your API key, for example `acme_live_8f3a9c2e7b1d44e0`.
