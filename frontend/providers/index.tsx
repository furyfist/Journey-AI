"use client";

import { createContext, useContext } from "react";
import { useAuth } from "@/hooks/useAuth";
import type { Session, User } from "@supabase/supabase-js";

interface AuthContextValue {
  user: User | null;
  session: Session | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  session: null,
  loading: true,
});

export function useAuthContext() {
  return useContext(AuthContext);
}

export default function Providers({ children }: { children: React.ReactNode }) {
  const auth = useAuth();

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}
