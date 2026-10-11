import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useQuasar } from "quasar";
import { api } from "@/boot/axios";
import type { Token, UserOut } from "@/types/api";

const TOKEN_KEY = "nomoni_token";

export const useAuthStore = defineStore("auth", () => {
  const $q = useQuasar();

  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const user = ref<UserOut | null>(null);

  const isLoggedIn = computed(() => !!token.value);

  async function login(email: string, password: string): Promise<void> {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const { data } = await api.post<Token>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    token.value = data.access_token;
    localStorage.setItem(TOKEN_KEY, data.access_token);
    await fetchMe();
  }

  async function register(payload: {
    email: string;
    password: string;
    name?: string | undefined;
  }): Promise<void> {
    const { data } = await api.post<Token>("/auth/register", payload);
    token.value = data.access_token;
    localStorage.setItem(TOKEN_KEY, data.access_token);
    await fetchMe();
  }

  async function fetchMe(): Promise<void> {
    try {
      const { data } = await api.get<UserOut>("/auth/me");
      user.value = data;
    } catch {
      logout();
    }
  }

  async function updateProfile(payload: {
    name?: string | null;
    currency?: string;
  }): Promise<void> {
    const { data } = await api.patch<UserOut>("/auth/me", payload);
    user.value = data;
    $q.notify({ type: "positive", message: "Perfil actualizado" });
  }

  function logout(): void {
    token.value = null;
    user.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    fetchMe,
    updateProfile,
    logout
  };
});
