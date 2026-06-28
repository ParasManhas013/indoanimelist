"use client";

import { useState } from "react";
import Link from "next/link";
import { submitRating, type User } from "@/lib/api";

interface Props {
  animeId: number;
  user: User | null;
  initialRating: number | null;
}

export function RatingWidget({ animeId, user, initialRating }: Props) {
  const [selected, setSelected] = useState<number | null>(initialRating);
  const [pendingString, setPendingString] = useState<string>(
    initialRating !== null ? String(initialRating) : "5.0"
  );
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user) {
    return (
      <div className="rating-widget">
        <h3>Rate this Anime</h3>
        <div className="rating-login-prompt">
          <Link href="/auth/login">Login</Link> or{" "}
          <Link href="/auth/register">Register</Link> to submit your rating
        </div>
      </div>
    );
  }

  const handleSubmit = async () => {
    const numericValue = parseFloat(pendingString);
    if (isNaN(numericValue) || numericValue < 1.0 || numericValue > 10.0) {
      setError("Please enter a valid rating between 1.0 and 10.0");
      return;
    }

    if (loading) return;
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await submitRating(animeId, numericValue);
      setSelected(numericValue);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit rating");
    } finally {
      setLoading(false);
    }
  };

  const handleBlur = () => {
    let val = parseFloat(pendingString);
    if (isNaN(val)) val = selected ?? 5.0;
    if (val < 1.0) val = 1.0;
    if (val > 10.0) val = 10.0;
    setPendingString(val.toString());
  };

  return (
    <div className="rating-widget">
      <h3>
        {selected ? `Your Rating: ${selected}/10` : "Rate this Anime"}
      </h3>

      <div className="rating-slider-container">
        <input
          type="range"
          min="1.0"
          max="10.0"
          step="0.01"
          value={pendingString}
          onChange={(e) => setPendingString(e.target.value)}
          className="rating-slider"
        />
        <input
          type="number"
          min="1.0"
          max="10.0"
          step="0.01"
          value={pendingString}
          onChange={(e) => setPendingString(e.target.value)}
          onBlur={handleBlur}
          className="rating-number-input"
        />
      </div>

      {error && (
        <div className="auth-error" style={{ marginBottom: "12px" }}>{error}</div>
      )}

      {success && (
        <div className="rating-success">
          ✅ Rating submitted successfully!
        </div>
      )}

      <button
        id="btn-submit-rating"
        className="rating-submit"
        onClick={handleSubmit}
        disabled={loading}
        style={{ marginTop: "12px" }}
      >
        {loading ? "Submitting..." : selected ? "Update Rating" : "Submit Rating"}
      </button>
    </div>
  );
}
