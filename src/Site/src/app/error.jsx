"use client";

import { useEffect } from "react";
import * as atatus from "../config/atatus";

export default function ErrorBoundary({ error, reset }) {
    useEffect(() => {
        atatus.addError(error, {
            tags: ["site_app_error"],
            digest: error?.digest,
            message: error?.message,
        });
        atatus.siteLogger.error(`Site error caught: ${error?.message || "Unknown error"}`, {
            stack: error?.stack,
            digest: error?.digest,
        });
    }, [error]);

    return (
        <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "60vh",
            padding: "2rem",
            textAlign: "center"
        }}>
            <h2 style={{ fontSize: "1.75rem", marginBottom: "1rem" }}>Something went wrong!</h2>
            <p style={{ color: "#888", marginBottom: "1.5rem", maxWidth: "500px" }}>
                An unexpected error occurred. It has been reported to our monitoring service.
            </p>
            <button
                onClick={() => reset()}
                style={{
                    backgroundColor: "var(--light-primary, #ff0000)",
                    color: "#fff",
                    border: "none",
                    padding: "0.6rem 1.4rem",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontWeight: 600
                }}
            >
                Try again
            </button>
        </div>
    );
}
