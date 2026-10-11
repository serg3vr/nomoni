import { defineBoot } from "#q-app";
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000"
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem("nomoni_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios;
  api.interceptors.response.use(
    response => response,
    error => {
      if (
        error.response?.status === 401 &&
        !error.config?.url?.includes("/auth/")
      ) {
        localStorage.removeItem("nomoni_token");
        window.location.replace("/auth/login");
      }
      return Promise.reject(error);
    }
  );
  app.provide("api", api);
});
