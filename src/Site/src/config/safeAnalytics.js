import { logEvent as firebaseLogEvent } from 'firebase/analytics';
import { sanitizeTelemetry } from './telemetryRedaction';

export function safeLogEvent(analytics, eventName, parameters) {
    try {
        firebaseLogEvent(analytics, eventName, sanitizeTelemetry(parameters));
    } catch {
        // Telemetry is best effort; malformed or unsafe event data is dropped.
    }
}
