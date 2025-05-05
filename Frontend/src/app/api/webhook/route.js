import Stripe from "stripe";
import { NextResponse, NextRequest } from "next/server";

const stripe = new Stripe(`${process.env.STRIPE_SECRET_KEY}`)

export async function POST(req) {
  const payload = await req.text()
  const res = JSON.parse(payload)
  const sig = req.headers.get("Stripe-Signature")
  const dateTime = new Date(res?.created * 1000).toLocaleDateString()
  const timeString = new Date(res?.created * 1000).toLocaleDateString()

  try {
    let event = stripe.webhooks.constructEvent(
      payload,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET,
    )
    console.log("event", event.type)
    //Events Listening to
    //charge.succeeded
    //payment_intent.succeeded
    //payment_intent.created
    switch (event.type) {
      case "payment_intent.created":
        const paymentIntentCreated = handlePaymentIntentCreated(event);
        if (!paymentIntentCreated) {
          return NextResponse.json({ status: 500 }, { error: "Payment not created" })
        }
      case "payment_intent.succeeded":
        const paymentIntentSucceeded = handlePaymentIntentSucceeded(event);
        if (!paymentIntentSucceeded) {
          return NextResponse.json({ status: 500 }, { error: "Payment not succeeded" })
        }
      case "charge.succeeded":
        const chargeSucceeded = handleChargeSucceeded(event);
        if (!chargeSucceeded) {
          return NextResponse.json({ status: 500 }, { error: "Charge not succeeded" })
        }
    }
    return NextResponse.json({ status: "Success", event: event.type })
  } catch (error) {
    return NextResponse.json({ status: "Failed", error })
  }
}


const handlePaymentIntentCreated = (event) => { 
  console.log(event.data.object)
  return true
}

const handlePaymentIntentSucceeded = (event) => {
  console.log(event)
  return true
} 

const handleChargeSucceeded = (event) => { 
  console.log(event)
  return true
}

//https://www.youtube.com/watch?v=AHRB_a-tONg&ab_channel=Jeremy
