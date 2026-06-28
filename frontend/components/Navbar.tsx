"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchMe, logout, type User } from "@/lib/api";

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMe().then((u) => {
      setUser(u);
      setLoading(false);
    });
  }, [pathname]);

  const handleLogout = async () => {
    await logout();
    setUser(null);
    router.push("/");
  };

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link href="/" className="navbar-logo">
          <div className="logo-icon">🎌</div>
          <div className="logo-text">
            Indo<span>Anime</span>List
          </div>
        </Link>

        <div className="navbar-links">
          <Link href="/" className={`nav-link ${pathname === "/" ? "active" : ""}`}>
            Leaderboard
          </Link>
          <Link href="/search" className={`nav-link ${pathname === "/search" ? "active" : ""}`}>
            Browse
          </Link>

          {!loading && (
            <>
              {user ? (
                <div className="nav-user">
                  <span className="nav-user-email">{user.email}</span>
                  <button id="btn-logout" className="btn-logout" onClick={handleLogout}>
                    Logout
                  </button>
                </div>
              ) : (
                <>
                  <Link href="/auth/login">
                    <button id="btn-nav-login" className="btn-nav-login">Login</button>
                  </Link>
                  <Link href="/auth/register">
                    <button id="btn-nav-register" className="btn-nav-register">Register</button>
                  </Link>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
