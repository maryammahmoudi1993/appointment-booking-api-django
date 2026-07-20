import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post("/api/auth/refresh/", {
            refresh,
          });
          localStorage.setItem("access_token", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      } else {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;

export interface User {
  id: number;
  email: string;
  username: string;
  role: "customer" | "staff" | "admin";
  phone: string;
}

export interface Service {
  id: number;
  name: string;
  description: string;
  duration_minutes: number;
  price: string;
  is_active: boolean;
}

export interface StaffProfile {
  id: number;
  user: number;
  username: string;
  full_name: string;
  bio: string;
  services_offered: number[];
  average_rating: number | null;
  review_count: number;
}

export interface AvailabilitySlot {
  start: string;
  end: string;
  available: boolean;
}

export interface AvailabilityResponse {
  date: string;
  available_slots: AvailabilitySlot[];
}

export interface Appointment {
  id: number;
  customer: number;
  customer_name: string;
  staff: number;
  staff_name: string;
  service: number;
  service_name: string;
  start_datetime: string;
  end_datetime: string;
  notes: string;
  status: "pending" | "confirmed" | "completed" | "cancelled";
  points_earned: number;
  has_review: boolean;
  discount_amount: string | null;
  created_at: string;
}

export interface Review {
  id: number;
  appointment: number;
  customer: number;
  customer_name: string;
  staff: number;
  staff_name: string;
  service_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface LoyaltyReward {
  id: number;
  name: string;
  description: string;
  points_cost: number;
  is_active: boolean;
}

export interface LoyaltyRedemption {
  id: number;
  reward: number;
  reward_name: string;
  points_spent: number;
  created_at: string;
}

export interface LoyaltySummary {
  balance: number;
  history: {
    appointment: number;
    service_name: string;
    points: number;
    date: string;
  }[];
  redemptions: LoyaltyRedemption[];
}

export interface PromoCode {
  id: number;
  code: string;
  description: string;
  discount_type: "percent" | "fixed";
  discount_value: string;
  is_active: boolean;
  max_redemptions: number | null;
  starts_at: string | null;
  ends_at: string | null;
  times_redeemed: number;
  revenue_influenced: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface WorkingHours {
  id: number;
  staff: number;
  weekday: number;
  start_time: string;
  end_time: string;
}

export interface TimeOff {
  id: number;
  staff: number;
  start_datetime: string;
  end_datetime: string;
  reason: string;
}

export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post("/auth/login/", data),
  register: (data: {
    username: string;
    email: string;
    password: string;
    password2: string;
    phone?: string;
  }) => api.post("/auth/register/", data),
  refresh: (refresh: string) => api.post("/auth/refresh/", { refresh }),
  logout: (refresh: string) => api.post("/auth/logout/", { refresh }),
  me: () => api.get<User>("/auth/me/"),
};

export const servicesApi = {
  list: (params?: { search?: string }) =>
    api.get<PaginatedResponse<Service>>("/services/", { params }),
  get: (id: number) => api.get<Service>(`/services/${id}/`),
  create: (data: Partial<Service>) => api.post("/services/", data),
  update: (id: number, data: Partial<Service>) =>
    api.put(`/services/${id}/`, data),
  delete: (id: number) => api.delete(`/services/${id}/`),
};

export const staffApi = {
  list: () => api.get<PaginatedResponse<StaffProfile>>("/staff/"),
  get: (id: number) => api.get<StaffProfile>(`/staff/${id}/`),
  availability: (userId: number, date: string) =>
    api.get<AvailabilityResponse>(`/staff/${userId}/availability/`, {
      params: { date },
    }),
  onboard: (data: {
    username: string;
    password: string;
    email?: string;
    first_name?: string;
    last_name?: string;
    phone_number?: string;
    bio?: string;
    services_offered?: number[];
  }) => api.post<StaffProfile>("/staff/onboard/", data),
  update: (
    id: number,
    data: Partial<Pick<StaffProfile, "bio" | "services_offered">>
  ) => api.patch<StaffProfile>(`/staff/${id}/`, data),
  delete: (id: number) => api.delete(`/staff/${id}/`),
};

export const workingHoursApi = {
  list: (staffUserId: number) =>
    api.get<PaginatedResponse<WorkingHours>>("/working-hours/", {
      params: { staff: staffUserId },
    }),
  create: (data: {
    staff: number;
    weekday: number;
    start_time: string;
    end_time: string;
  }) => api.post<WorkingHours>("/working-hours/", data),
  update: (
    id: number,
    data: Partial<Pick<WorkingHours, "start_time" | "end_time">>
  ) => api.patch<WorkingHours>(`/working-hours/${id}/`, data),
  delete: (id: number) => api.delete(`/working-hours/${id}/`),
};

export const timeOffApi = {
  list: (staffUserId: number) =>
    api.get<PaginatedResponse<TimeOff>>("/time-off/", {
      params: { staff: staffUserId },
    }),
  create: (data: {
    staff: number;
    start_datetime: string;
    end_datetime: string;
    reason?: string;
  }) => api.post<TimeOff>("/time-off/", data),
  delete: (id: number) => api.delete(`/time-off/${id}/`),
};

export const appointmentsApi = {
  list: (params?: {
    status?: string;
    staff?: number;
    service?: number;
    date_from?: string;
    date_to?: string;
    page_size?: number;
  }) => api.get<PaginatedResponse<Appointment>>("/appointments/", { params }),
  get: (id: number) => api.get<Appointment>(`/appointments/${id}/`),
  create: (data: {
    customer: number;
    staff: number;
    service: number;
    start_datetime: string;
    end_datetime: string;
    notes?: string;
    promo_code?: string;
  }) => api.post<Appointment>("/appointments/", data),
  update: (id: number, data: Partial<Appointment>) =>
    api.patch(`/appointments/${id}/`, data),
  cancel: (id: number) => api.post(`/appointments/${id}/cancel/`),
  confirm: (id: number) => api.patch(`/appointments/${id}/confirm/`),
  complete: (id: number) => api.patch(`/appointments/${id}/complete/`),
};

export const reviewsApi = {
  list: (params?: { staff?: number }) =>
    api.get<PaginatedResponse<Review>>("/reviews/", { params }),
  create: (data: { appointment: number; rating: number; comment?: string }) =>
    api.post<Review>("/reviews/", data),
};

export const loyaltyApi = {
  summary: () => api.get<LoyaltySummary>("/loyalty/summary/"),
  rewards: () => api.get<PaginatedResponse<LoyaltyReward>>("/loyalty/rewards/"),
  redeem: (rewardId: number) =>
    api.post<LoyaltyRedemption>(`/loyalty/rewards/${rewardId}/redeem/`),
};

export const promotionsApi = {
  list: () => api.get<PaginatedResponse<PromoCode>>("/promotions/"),
  create: (data: {
    code: string;
    description?: string;
    discount_type: "percent" | "fixed";
    discount_value: string;
    max_redemptions?: number | null;
  }) => api.post<PromoCode>("/promotions/", data),
  update: (id: number, data: Partial<Pick<PromoCode, "is_active">>) =>
    api.patch<PromoCode>(`/promotions/${id}/`, data),
  delete: (id: number) => api.delete(`/promotions/${id}/`),
  validate: (code: string) =>
    api.post<{
      code: string;
      discount_type: "percent" | "fixed";
      discount_value: string;
    }>("/promotions/validate/", { code }),
};
