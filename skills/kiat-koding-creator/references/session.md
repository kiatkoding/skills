# Sesi 1:1 (session lessons)

A Sesi 1:1 is a lesson of kind `session`: a video call with the course's instructor that a learner books on the instructor's free hours and pays for apart from the course. The course price does not include it.

## How learners use it

- It sits in the curriculum like any lesson, marked optional with its price, often after a few chapters (a review of the project so far, a chance to ask about the last chapters).
- The learner may skip it. It never locks the lessons after it, and it counts toward neither progress nor the certificate.
- Once they reach it, they pick a day and a start time from the free slots and the topics to talk through, then pay with the course's own payment method (Midtrans or QRIS DANA). A coupon that covers sessions can lower the price.
- The topics are drawn by the Kiat Koding AI for each learner: from the agenda, the lessons since the previous Sesi 1:1 (or the course start), and that learner's Latihan and Submission results in them. All start ticked, the learner may untick some and add one of their own, and the instructor sees them with the reason behind each, drawn again a day before the session.
- A paid booking gets a Google Calendar event with its own Meet link and reminders a day and an hour before. The learner may move it once, up to 24 hours before it starts. After the session they see the instructor's notes, and they can book another.

## What you set

- `minutes`: the length, 15 to 180, a multiple of 5.
- `price_idr`: the price of one session in rupiah, 0 for free.
- `photo`: the instructor's photo in the page's header. `"google"` for their Google profile photo, or the `/uploads/images/` path of a photo the creator gives you, uploaded with `create_image_upload`. Ask the creator which. Their choice becomes the default for their later sessions; leave it out to use that default, which `get_lesson` shows as `session.photo_default`.
- `agenda`: Markdown on what the session is for and how to prepare. Keep it short and general: the AI takes it as the direction for each learner's topics, so do not list topics yourself.
- `hours`: leave it out to use the instructor's schedule, which they set once in the admin and which every session of theirs shares. Send it only when this lesson should have its own free hours: a list of `{ "day": 1, "from": "19:00", "to": "21:00" }`, `day` 1 Monday to 7 Sunday, times in WIB. `get_lesson` shows the instructor's schedule as `session.instructor_hours`; when it is empty you must send `hours`.

Slots are the free hours cut into sessions of `minutes` with a 15-minute break after each, from 12 hours ahead to 30 days out, minus what the instructor already has (other sessions, live sessions).

## The creator decides the terms

- Ask the creator what to charge, how long a session runs and when they are free before you add one. Never pick a price, a length or hours yourself, and never add a session the creator did not ask for.
- You cannot choose the payment method: a session takes the course's own.
- A session you add, or whose price, length or hours you change, stays closed to bookings until the creator opens the lesson in the admin and saves it. The answer's `session.confirmed` is then false. Tell the creator this and give them `session.admin_url`. Changing only the agenda keeps it open.

## Example

```json
{
  "section_id": 812,
  "title": "Sesi 1:1: review project bab 1 sampai 3",
  "kind": "session",
  "minutes": 45,
  "price_idr": 150000,
  "agenda": "Kita bahas project dari bab 1 sampai 3: bagian yang masih bikin bingung dan langkah berikutnya. Siapkan link repo kamu."
}
```
