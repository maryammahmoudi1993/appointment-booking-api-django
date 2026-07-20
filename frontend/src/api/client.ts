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
}

export interface AvailabilitySlot {
  start: string;
  end: string;
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
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
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
};

export const appointmentsApi = {
  list: (params?: { status?: string }) =>
    api.get<PaginatedResponse<Appointment>>("/appointments/", { params }),
  get: (id: number) => api.get<Appointment>(`/appointments/${id}/`),
  create: (data: {
    customer: number;
    staff: number;
    service: number;
    start_datetime: string;
    end_datetime: string;
    notes?: string;
  }) => api.post("/appointments/", data),
  update: (id: number, data: Partial<Appointment>) =>
    api.patch(`/appointments/${id}/`, data),
  cancel: (id: number) => api.post(`/appointments/${id}/cancel/`),
  confirm: (id: number) => api.patch(`/appointments/${id}/confirm/`),
  complete: (id: number) => api.patch(`/appointments/${id}/complete/`),
};
