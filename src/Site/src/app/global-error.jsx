"use client";

import { useEffect } from "react";
import * as atatus from "../config/atatus";

export default function GlobalError({ error, reset }) {
    useEffect(() => {
        atatus.addError(error, {
            tags: ["site_global_error"],
            digest: error?.digest,
            message: error?.message,
        });
        atatus.siteLogger.error(`Global error caught: ${error?.message || "Unknown global error"}`, {
            stack: error?.stack,
            digest: error?.digest,
        });
    }, [error]);

    return (
        <html lang="en">
            <body>
                <div style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    minHeight: "100vh",
                    padding: "2rem",
                    textAlign: "center",
                    fontFamily: "sans-serif"
                }}>
                    <h2>Application Error</h2>
                    <p style={{ color: "#666", marginBottom: "1.5rem" }}>
                        A critical error occurred. Please try reloading the page.
                    </p>
                    <button
                        onClick={() => reset()}
                        style={{
                            backgroundColor: "#ff0000",
                            color: "#fff",
                            border: "none",
                            padding: "0.6rem 1.4rem",
                            borderRadius: "6px",
                            cursor: "pointer"
                        }}
                    >
                        Reload
                    </button>
                </div>
            </body>
        </html>
    );
}
