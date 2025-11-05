# RailServe Booking Flowchart

Detailed flowcharts for the complete booking process from search to confirmation.

---

## Complete Booking Flow

```
                        START
                          │
                          ▼
              ┌─────────────────────┐
              │   User visits       │
              │   Homepage (/)      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Search Form        │
              │  • From Station     │
              │  • To Station       │
              │  • Journey Date     │
              └──────────┬──────────┘
                         │
                         ▼ Submit
              ┌─────────────────────┐
              │  POST /search_trains│
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  search_trains()    │
              │  in utils.py        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Query Database:    │
              │  • Find trains      │
              │  • Check routes     │
              │  • Calculate        │
              │    availability     │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ No trains│  │  Trains  │  │  Error   │
    │  found   │  │  found   │  │ occurred │
    └─────┬────┘  └─────┬────┘  └─────┬────┘
          │             │             │
          ▼             ▼             ▼
    Show error    Show results    Show error
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  Display Results    │
              │  • Train list       │
              │  • Seat availability│
              │  • Fare info        │
              │  • Book buttons     │
              └──────────┬──────────┘
                         │
                         ▼ Click "Book Now"
              ┌─────────────────────┐
              │ GET /booking/book/  │
              │     <train_id>      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Check if logged in │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           │                           │
           ▼ NO                        ▼ YES
    ┌──────────┐              ┌──────────────┐
    │ Redirect │              │ book_ticket()│
    │ to login │              │ in booking.py│
    └─────┬────┘              └──────┬───────┘
          │                          │
          ▼ After login              │
    ┌──────────┐                     │
    │ Return   │                     │
    │ to book  │                     │
    └─────┬────┘                     │
          │                          │
          └────────────┬─────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │  Store in session:  │
              │  • train_id         │
              │  • from_station_id  │
              │  • to_station_id    │
              │  • journey_date     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Render booking     │
              │  form (book_ticket  │
              │  .html)             │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  User fills form:   │
              │  • Num passengers   │
              │  • Names, ages      │
              │  • Gender, ID proof │
              │  • Coach class      │
              │  • Berth preference │
              └──────────┬──────────┘
                         │
                         ▼ Submit
              ┌─────────────────────┐
              │ POST /booking/      │
              │   seat_selection    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  seat_selection()   │
              │  in booking.py      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Validate form data │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           │                           │
           ▼ Invalid                   ▼ Valid
    ┌──────────┐              ┌──────────────┐
    │  Flash   │              │ Check seat   │
    │  error   │              │ availability │
    └─────┬────┘              └──────┬───────┘
          │                          │
          ▼                          │
    Show form again    ┌─────────────┼─────────────┐
          │            │                           │
          └────────────┘             ▼ Available   ▼ Not Available
                            ┌──────────────┐  ┌──────────────┐
                            │ Call Seat    │  │ Add to       │
                            │ Allocator    │  │ Waitlist     │
                            └──────┬───────┘  └──────┬───────┘
                                   │                 │
                                   ▼                 │
                            ┌──────────────┐         │
                            │ Assign:      │         │
                            │ • Coach      │         │
                            │ • Seat number│         │
                            │ • Berth type │         │
                            └──────┬───────┘         │
                                   │                 │
                                   └────────┬────────┘
                                            │
                                            ▼
                              ┌───────────────────────┐
                              │  Calculate fare:      │
                              │  distance × fare/km   │
                              │  × passengers         │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Create Booking:      │
                              │  • Generate PNR       │
                              │  • Status: pending    │
                              │  • Store in DB        │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Create Passenger(s): │
                              │  • Link to booking    │
                              │  • Seat details       │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Commit transaction   │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Redirect to payment  │
                              │  /payment/process/    │
                              │  <booking_id>         │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  process_payment()    │
                              │  in payment.py        │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Create Payment:      │
                              │  • booking_id         │
                              │  • amount             │
                              │  • status: pending    │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  Render payment.html  │
                              │  (or redirect to      │
                              │   payment gateway)    │
                              └──────────┬────────────┘
                                         │
                                         ▼
                              ┌───────────────────────┐
                              │  User completes       │
                              │  payment              │
                              └──────────┬────────────┘
                                         │
                       ┌─────────────────┼─────────────────┐
                       │                                   │
                       ▼ Success                           ▼ Failure
            ┌────────────────────┐              ┌────────────────────┐
            │ POST /payment/     │              │ POST /payment/     │
            │      success       │              │      failure       │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ payment_success()  │              │ payment_failure()  │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Update Booking:    │              │ Update Booking:    │
            │ status=confirmed   │              │ status=cancelled   │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Update Payment:    │              │ Update Payment:    │
            │ status=success     │              │ status=failed      │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Update Seat        │              │ Restore Seat       │
            │ Availability       │              │ Availability       │
            │ (decrease)         │              │ (rollback)         │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Generate PDF       │              │ Display error      │
            │ ticket             │              │ message            │
            └──────────┬─────────┘              └──────────┬─────────┘
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Send confirmation  │              │ Offer retry option │
            │ email (optional)   │              └──────────┬─────────┘
            └──────────┬─────────┘                         │
                       │                                   │
                       ▼                                   ▼
            ┌────────────────────┐              ┌────────────────────┐
            │ Display success:   │              │    END (Failure)   │
            │ • PNR              │              └────────────────────┘
            │ • Download link    │
            │ • Journey details  │
            └──────────┬─────────┘
                       │
                       ▼
            ┌────────────────────┐
            │   END (Success)    │
            └────────────────────┘
```

---

## Seat Allocation Algorithm Flowchart

```
                    START
                      │
                      ▼
          ┌──────────────────────┐
          │  Input:              │
          │  • Train ID          │
          │  • Passengers list   │
          │  • Coach class       │
          │  • Preferences       │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Get available seats │
          │  for coach class     │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │                         │
        ▼ Seats available         ▼ No seats
┌───────────────┐         ┌───────────────┐
│ Allocate Seats│         │ Add to        │
└───────┬───────┘         │ Waitlist      │
        │                 └───────┬───────┘
        ▼                         │
For each passenger:               │
┌───────────────┐                 │
│ Get preference│                 │
│ (Lower/Middle/│                 │
│  Upper/Side)  │                 │
└───────┬───────┘                 │
        │                         │
        ▼                         │
┌───────────────┐                 │
│ Find matching │                 │
│ seat if       │                 │
│ available     │                 │
└───────┬───────┘                 │
        │                         │
   ┌────┼────┐                    │
   │         │                    │
   ▼ Found   ▼ Not found          │
┌──────┐  ┌──────┐                │
│Assign│  │Assign│                │
│exact │  │next  │                │
│match │  │avail │                │
└───┬──┘  └───┬──┘                │
    │         │                   │
    └────┬────┘                   │
         │                        │
         ▼                        │
┌─────────────────┐               │
│ Assign:         │               │
│ • Coach (S1/B2) │               │
│ • Seat (45)     │               │
│ • Berth (Lower) │               │
└────────┬────────┘               │
         │                        │
         ▼                        │
┌─────────────────┐               │
│ Mark seat as    │               │
│ allocated       │               │
└────────┬────────┘               │
         │                        │
         └────────────────────────┘
                  │
                  ▼
           ┌────────────┐
           │    END     │
           └────────────┘
```

---

## Waitlist Auto-Confirmation Flowchart

```
                    START
                      │
                      ▼
          ┌──────────────────────┐
          │  Trigger Event:      │
          │  • Booking cancelled │
          │  • Chart preparation │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Check waitlist for  │
          │  this train/date/    │
          │  class               │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │                         │
        ▼ Waitlist exists         ▼ No waitlist
┌───────────────┐         ┌───────────────┐
│ Get first     │         │    END        │
│ waitlisted    │         └───────────────┘
│ booking (FIFO)│
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Check seat    │
│ availability  │
└───────┬───────┘
        │
   ┌────┼────┐
   │         │
   ▼ Yes     ▼ No
┌──────┐  ┌──────┐
│Confirm│  │Keep  │
│booking│  │in WL │
└───┬──┘  └───┬──┘
    │         │
    ▼         ▼
┌──────────────┐  ┌─────┐
│ Update:      │  │ END │
│ • status →   │  └─────┘
│   confirmed  │
│ • seat alloc │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│ Send email   │
│ notification │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│ Repeat for   │
│ next waitlist│
│ booking      │
└───────┬──────┘
        │
        ▼
     ┌─────┐
     │ END │
     └─────┘
```

---

## Tatkal Booking Flowchart

```
                    START
                      │
                      ▼
          ┌──────────────────────┐
          │  User selects        │
          │  Tatkal booking      │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Get current time    │
          │  and coach class     │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │                         │
        ▼ AC class                ▼ Non-AC class
┌───────────────┐         ┌───────────────┐
│ Check if time │         │ Check if time │
│ >= 10:00 AM   │         │ >= 11:00 AM   │
└───────┬───────┘         └───────┬───────┘
        │                         │
   ┌────┼────┐              ┌────┼────┐
   │         │              │         │
   ▼ Yes     ▼ No           ▼ Yes     ▼ No
┌──────┐  ┌──────┐      ┌──────┐  ┌──────┐
│Allow │  │Block │      │Allow │  │Block │
│booking│  │      │      │booking│  │      │
└───┬──┘  └───┬──┘      └───┬──┘  └───┬──┘
    │         │              │         │
    │         ▼              │         ▼
    │  ┌──────────┐          │  ┌──────────┐
    │  │Show error│          │  │Show error│
    │  │"Tatkal   │          │  │"Tatkal   │
    │  │opens at  │          │  │opens at  │
    │  │10:00 AM" │          │  │11:00 AM" │
    │  └────┬─────┘          │  └────┬─────┘
    │       │                │       │
    │       ▼                │       ▼
    │     ┌─────┐            │     ┌─────┐
    │     │ END │            │     │ END │
    │     └─────┘            │     └─────┘
    │                        │
    └────────────┬───────────┘
                 │
                 ▼
      ┌──────────────────┐
      │ Check Tatkal     │
      │ quota available  │
      └──────────┬───────┘
                 │
     ┌───────────┼───────────┐
     │                       │
     ▼ Available             ▼ Full
┌─────────┐          ┌──────────────┐
│Calculate│          │ Show "Tatkal │
│premium  │          │  quota full" │
│fare     │          └──────┬───────┘
│(1.3x)   │                 │
└────┬────┘                 ▼
     │                    ┌─────┐
     ▼                    │ END │
┌─────────┐               └─────┘
│Proceed  │
│with     │
│booking  │
│flow     │
└────┬────┘
     │
     ▼
   ┌─────┐
   │ END │
   └─────┘
```

---

## PNR Enquiry Flowchart

```
          START
            │
            ▼
┌──────────────────────┐
│ User enters PNR      │
│ (10-digit number)    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ POST /pnr_enquiry    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Query database:      │
│ Booking.query        │
│ .filter_by(pnr=...)  │
└──────────┬───────────┘
           │
  ┌────────┼────────┐
  │                 │
  ▼ Found           ▼ Not Found
┌──────┐      ┌──────────────┐
│ Get  │      │ Show "Invalid│
│booking│      │  PNR" error  │
└───┬──┘      └──────┬───────┘
    │                │
    ▼                ▼
┌─────────────┐   ┌─────┐
│ Get related:│   │ END │
│ • Passengers│   └─────┘
│ • Train     │
│ • Stations  │
│ • Payment   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Display:        │
│ • PNR status    │
│ • Train details │
│ • Passengers    │
│ • Seats         │
│ • Journey date  │
│ • Booking status│
└────────┬────────┘
         │
         ▼
      ┌─────┐
      │ END │
      └─────┘
```

---

**Last Updated:** November 2025  
**Purpose:** Visual process flows for development reference  
**Format:** ASCII art flowcharts
