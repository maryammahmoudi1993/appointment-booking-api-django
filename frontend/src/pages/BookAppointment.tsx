import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  servicesApi,
  staffApi,
  appointmentsApi,
  promotionsApi,
  type Service,
  type StaffProfile,
  type AvailabilitySlot,
} from "../api/client";

interface AppliedPromo {
  code: string;
  discount_type: "percent" | "fixed";
  discount_value: string;
}

function computeDiscount(promo: AppliedPromo, price: number): number {
  const value = Number(promo.discount_value);
  const discount = promo.discount_type === "percent" ? (price * value) / 100 : value;
  return Math.min(discount, price);
}

type Step = "service" | "staff" | "datetime" | "confirm" | "done";

const STEPS: { key: Step; label: string }[] = [
  { key: "service", label: "Service" },
  { key: "staff", label: "Specialist" },
  { key: "datetime", label: "Date & Time" },
  { key: "confirm", label: "Confirm" },
];

function extractErrorMessage(err: any, fallback: string): string {
  const data = err.response?.data;
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail[0];
  const firstFieldError = Object.values(data).flat()[0];
  return typeof firstFieldError === "string" ? firstFieldError : fallback;
}

export default function BookAppointment() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState<Step>("service");
  const [error, setError] = useState("");

  const [services, setServices] = useState<Service[]>([]);
  const [staffList, setStaffList] = useState<StaffProfile[]>([]);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [selectedStaff, setSelectedStaff] = useState<StaffProfile | null>(
    null
  );
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState<AvailabilitySlot | null>(
    null
  );
  const [notes, setNotes] = useState("");
  const [promoInput, setPromoInput] = useState("");
  const [appliedPromo, setAppliedPromo] = useState<AppliedPromo | null>(null);
  const [promoError, setPromoError] = useState("");
  const [applyingPromo, setApplyingPromo] = useState(false);

  useEffect(() => {
    servicesApi.list().then((res) => setServices(res.data.results));
    staffApi.list().then((res) => setStaffList(res.data.results));
  }, []);

  // Pre-select service/staff when arriving from a "Book" link on the
  // Services or Staff page (e.g. /book?staff=2) and jump ahead a step.
  useEffect(() => {
    if (!services.length && !staffList.length) return;

    const serviceId = searchParams.get("service");
    const staffId = searchParams.get("staff");
    const preselectedService = serviceId
      ? services.find((s) => s.id === Number(serviceId))
      : null;
    const preselectedStaff = staffId
      ? staffList.find((s) => s.id === Number(staffId))
      : null;

    if (preselectedService) setSelectedService(preselectedService);
    if (preselectedStaff) setSelectedStaff(preselectedStaff);

    if (preselectedService && preselectedStaff) setStep("datetime");
    else if (preselectedService) setStep("staff");
    else if (preselectedStaff) setStep("service");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [services, staffList]);

  useEffect(() => {
    if (selectedStaff && selectedDate) {
      staffApi
        .availability(selectedStaff.user, selectedDate)
        .then((res) => setSlots(res.data.available_slots))
        .catch(() => setSlots([]));
    }
  }, [selectedStaff, selectedDate]);

  const handleApplyPromo = async () => {
    if (!promoInput.trim()) return;
    setPromoError("");
    setApplyingPromo(true);
    try {
      const res = await promotionsApi.validate(promoInput.trim());
      setAppliedPromo(res.data);
    } catch (err: any) {
      setAppliedPromo(null);
      setPromoError(extractErrorMessage(err, "Invalid promo code."));
    } finally {
      setApplyingPromo(false);
    }
  };

  const handleConfirm = async () => {
    if (!selectedService || !selectedStaff || !selectedSlot || !user) return;
    setError("");
    setSubmitting(true);
    try {
      await appointmentsApi.create({
        customer: user.id,
        staff: selectedStaff.user,
        service: selectedService.id,
        start_datetime: `${selectedDate}T${selectedSlot.start}`,
        end_datetime: `${selectedDate}T${selectedSlot.end}`,
        notes,
        promo_code: appliedPromo?.code,
      });
      setStep("done");
    } catch (err: any) {
      setError(extractErrorMessage(err, "Booking failed. Please try again."));
    } finally {
      setSubmitting(false);
    }
  };

  const today = new Date().toISOString().split("T")[0];
  const stepIndex = STEPS.findIndex((s) => s.key === step);

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <h2 className="font-display text-2xl font-bold text-brand-900">
        Book an Appointment
      </h2>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      <div className="mt-8">
        {step !== "done" && (
          <div className="mb-10 flex items-center">
            {STEPS.map((s, i) => (
              <div key={s.key} className="flex flex-1 items-center last:flex-none">
                <div className="flex flex-col items-center gap-1.5">
                  <span
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${
                      i < stepIndex
                        ? "bg-brand-600 text-white"
                        : i === stepIndex
                          ? "bg-brand-600 text-white ring-4 ring-brand-100"
                          : "bg-gray-100 text-gray-400"
                    }`}
                  >
                    {i < stepIndex ? "✓" : i + 1}
                  </span>
                  <span
                    className={`text-xs font-medium ${
                      i <= stepIndex ? "text-brand-800" : "text-gray-400"
                    }`}
                  >
                    {s.label}
                  </span>
                </div>
                {i < STEPS.length - 1 && (
                  <div
                    className={`mx-2 h-0.5 flex-1 ${
                      i < stepIndex ? "bg-brand-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        )}

        {step === "service" && (
          <div className="grid gap-4 sm:grid-cols-2">
            {services.map((s) => (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedService(s);
                  setStep(selectedStaff ? "datetime" : "staff");
                }}
                className="rounded-xl border border-brand-100 bg-white p-4 text-left shadow-sm transition hover:border-brand-400 hover:shadow-md"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-900">{s.name}</span>
                  <span className="font-display font-bold text-brand-600">
                    ${s.price}
                  </span>
                </div>
                <div className="mt-1 text-sm text-gray-500">
                  {s.duration_minutes} min
                </div>
              </button>
            ))}
          </div>
        )}

        {step === "staff" && (
          <div className="grid gap-4 sm:grid-cols-2">
            {staffList.map((s) => (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedStaff(s);
                  setStep("datetime");
                }}
                className="rounded-xl border border-brand-100 bg-white p-4 text-left shadow-sm transition hover:border-brand-400 hover:shadow-md"
              >
                <div className="font-semibold text-gray-900">{s.full_name}</div>
                <div className="mt-1 text-sm text-gray-600">{s.bio}</div>
              </button>
            ))}
          </div>
        )}

        {step === "datetime" && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Date
              </label>
              <input
                type="date"
                value={selectedDate}
                min={today}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setSelectedSlot(null);
                }}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
            </div>
            {selectedDate && (
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Available Times
                </label>
                {slots.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">
                    No available slots for this date.
                  </p>
                ) : (
                  <div className="mt-2 grid grid-cols-4 gap-2">
                    {slots.map((slot) => (
                      <button
                        key={slot.start}
                        disabled={!slot.available}
                        onClick={() => setSelectedSlot(slot)}
                        className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
                          !slot.available
                            ? "cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300 line-through"
                            : selectedSlot?.start === slot.start
                              ? "border-brand-600 bg-brand-50 text-brand-700"
                              : "border-gray-200 bg-white text-gray-700 hover:border-brand-300"
                        }`}
                      >
                        {slot.start.slice(0, 5)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {selectedSlot && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Notes (optional)
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Promo code (optional)
                  </label>
                  {appliedPromo ? (
                    <div className="mt-1 flex items-center justify-between rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-sm text-brand-800">
                      <span>
                        <strong>{appliedPromo.code}</strong> applied —{" "}
                        {appliedPromo.discount_type === "percent"
                          ? `${appliedPromo.discount_value}% off`
                          : `$${appliedPromo.discount_value} off`}
                      </span>
                      <button
                        onClick={() => {
                          setAppliedPromo(null);
                          setPromoInput("");
                        }}
                        className="text-xs font-medium text-brand-600 hover:text-brand-800"
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <div className="mt-1 flex gap-2">
                      <input
                        type="text"
                        value={promoInput}
                        onChange={(e) => setPromoInput(e.target.value)}
                        placeholder="e.g. WELCOME15"
                        className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm uppercase focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      />
                      <button
                        onClick={handleApplyPromo}
                        disabled={applyingPromo}
                        className="rounded-lg border border-brand-200 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50 disabled:opacity-50"
                      >
                        {applyingPromo ? "..." : "Apply"}
                      </button>
                    </div>
                  )}
                  {promoError && (
                    <p className="mt-1 text-xs text-red-700">{promoError}</p>
                  )}
                </div>
                <button
                  onClick={() => setStep("confirm")}
                  className="rounded-full bg-brand-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
                >
                  Review Booking
                </button>
              </>
            )}
          </div>
        )}

        {step === "confirm" && selectedService && selectedStaff && selectedSlot && (
          <div className="space-y-4 rounded-2xl border border-brand-100 bg-white p-6 shadow-sm">
            <h3 className="font-display text-lg font-semibold text-brand-900">
              Confirm Your Booking
            </h3>
            <dl className="space-y-2 text-sm">
              {[
                ["Service", selectedService.name],
                ["Specialist", selectedStaff.full_name],
                ["Date", selectedDate],
                [
                  "Time",
                  `${selectedSlot.start.slice(0, 5)} - ${selectedSlot.end.slice(0, 5)}`,
                ],
                ["Price", `$${selectedService.price}`],
                ...(appliedPromo
                  ? [
                      [
                        `Promo (${appliedPromo.code})`,
                        `-$${computeDiscount(appliedPromo, Number(selectedService.price)).toFixed(2)}`,
                      ],
                      [
                        "Total",
                        `$${Math.max(
                          0,
                          Number(selectedService.price) -
                            computeDiscount(appliedPromo, Number(selectedService.price))
                        ).toFixed(2)}`,
                      ],
                    ]
                  : []),
                ...(notes ? [["Notes", notes]] : []),
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-4">
                  <dt className="font-medium text-gray-500">{label}</dt>
                  <dd className="text-right text-gray-900">{value}</dd>
                </div>
              ))}
            </dl>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep("datetime")}
                className="rounded-full border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Back
              </button>
              <button
                onClick={handleConfirm}
                disabled={submitting}
                className="rounded-full bg-brand-600 px-6 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
              >
                {submitting ? "Booking..." : "Confirm & Book"}
              </button>
            </div>
          </div>
        )}

        {step === "done" && (
          <div className="rounded-2xl border border-brand-200 bg-brand-50 p-8 text-center">
            <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 text-xl text-white">
              ✓
            </span>
            <h3 className="mt-4 font-display text-xl font-semibold text-brand-900">
              Booking Confirmed!
            </h3>
            <p className="mt-2 text-brand-700">
              Your appointment has been booked successfully.
            </p>
            <div className="mt-6 flex justify-center gap-4">
              <button
                onClick={() => navigate("/my-bookings")}
                className="rounded-full bg-brand-600 px-6 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
              >
                View My Bookings
              </button>
              <button
                onClick={() => {
                  setStep("service");
                  setSelectedService(null);
                  setSelectedStaff(null);
                  setSelectedDate("");
                  setSelectedSlot(null);
                  setNotes("");
                  setPromoInput("");
                  setAppliedPromo(null);
                }}
                className="rounded-full border border-brand-200 bg-white px-6 py-2 text-sm font-medium text-brand-800 hover:bg-brand-50"
              >
                Book Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
