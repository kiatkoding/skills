# Sesi 1:1 (session lessons)

A Sesi 1:1 is a lesson of kind `session`: a video call with the course's instructor that a learner books on the instructor's free hours and pays for apart from the course. The course price does not include it.

## How learners use it

- It sits in the curriculum like any lesson, marked optional with its price, often after a few chapters (a review of the project so far, a chance to ask about the last chapters).
- The learner may skip it. It never locks the lessons after it, and it counts toward neither progress nor the certificate.
- Once they reach it, they pick a day and a start time from the free slots, answer the lesson's `questions`, and pay with the course's own payment method (Midtrans or QRIS DANA). A coupon that covers sessions can lower the price.
- A paid booking gets a Google Calendar event with its own Meet link and reminders a day and an hour before. The learner may move it once, up to 24 hours before it starts. After the session they see the instructor's notes, and they can book another.

## What you set

- `minutes`: the length, 15 to 180, a multiple of 5.
- `price_idr`: the price of one session in rupiah, 0 for free.
- `agenda`: Markdown on what the session covers and how to prepare. Keep it short.
- `questions`: up to 3 questions the learner answers when booking, such as what they want to go through or a link to their code.
- `hours`: leave it out to use the instructor's schedule, which they set once in the admin and which every session of theirs shares. Send it only when this lesson should have its own free hours: a list of `{ "day": 1, "from": "19:00", "to": "21:00" }`, `day` 1 Monday to 7 Sunday, times in WIB. `get_lesson` shows the instructor's schedule as `session.instructor_hours`; when it is empty you must send `hours`.

Slots are the free hours cut into sessions of `minutes` with a 15-minute break after each, from 12 hours ahead to 30 days out, minus what the instructor already has (other sessions, live sessions).

## The creator decides the terms

- Ask the creator what to charge, how long a session runs and when they are free before you add one. Never pick a price, a length or hours yourself, and never add a session the creator did not ask for.
- You cannot choose the payment method: a session takes the course's own.
- A session you add, or whose price, length or hours you change, stays closed to bookings until the creator opens the lesson in the admin and saves it. The answer's `session.confirmed` is then false. Tell the creator this and give them `session.admin_url`. Changing only the agenda or the questions keeps it open.

## Example

```json
{
  "section_id": 812,
  "title": "Sesi 1:1: review project bab 1 sampai 3",
  "kind": "session",
  "minutes": 45,
  "price_idr": 150000,
  "agenda": "Kita bahas project dari bab 1 sampai 3: struktur foldernya, bagian yang masih bikin bingung, dan langkah berikutnya. Siapkan link repo kamu.",
  "questions": ["Link repo project kamu?", "Bagian mana yang paling ingin kamu bahas?"]
}
```
