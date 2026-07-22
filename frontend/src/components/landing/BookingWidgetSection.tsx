import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function BookingWidgetSection() {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");

  const timeSlots = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
    "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
  ];

  return (
    <section className="py-20 bg-blush" aria-labelledby="booking-heading">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="inline-flex items-center rounded-full border border-champagne/30 bg-white/60 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-champagne-dark">
            Book Now
          </span>
          <h2
            id="booking-heading"
            className="mt-4 font-display text-3xl font-bold text-charcoal sm:text-4xl"
          >
            Reserve Your Experience
          </h2>
          <p className="mt-4 text-charcoal-light">
            Select your preferred date and time, and we&apos;ll take care of the rest.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-lg">
          <div className="rounded-xl border border-champagne/20 bg-white p-8 shadow-sm">
            <div className="space-y-6">
              {/* Date picker */}
              <div>
                <label htmlFor="booking-date" className="block text-sm font-semibold text-charcoal mb-2">
                  Select Date
                </label>
                <input
                  id="booking-date"
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  min={new Date().toISOString().split("T")[0]}
                  className="w-full rounded-lg border border-champagne/30 bg-cream/50 px-4 py-3 text-sm text-charcoal focus:border-champagne focus:outline-none focus:ring-2 focus:ring-champagne/20"
                />
              </div>

              {/* Time slots */}
              <div>
                <label className="block text-sm font-semibold text-charcoal mb-2">
                  Select Time
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {timeSlots.map((time) => (
                    <button
                      key={time}
                      type="button"
                      onClick={() => setSelectedTime(time)}
                      className={`rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                        selectedTime === time
                          ? "bg-rosegold-gradient text-white shadow-sm"
                          : "border border-champagne/20 bg-cream/30 text-charcoal hover:border-champagne/40 hover:bg-champagne/10"
                      }`}
                    >
                      {time}
                    </button>
                  ))}
                </div>
              </div>

              {/* Book button */}
              <Link
                to={user ? "/book" : "/register"}
                className="block w-full rounded-full bg-rosegold-gradient py-3.5 text-center text-sm font-semibold text-white shadow-md transition-all hover:shadow-lg hover:scale-[1.01] active:scale-[0.99]"
              >
                {user ? "Continue to Booking" : "Sign Up to Book"}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
