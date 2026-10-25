import test from 'node:test';
import assert from 'node:assert/strict';
import {
    sanitizeTelemetry,
    sanitizeTelemetryString,
    sanitizeTelemetryUrl,
    isSensitiveInput,
} from '../src/lib/telemetryRedaction.js';

test('redacts structured credentials, cookie records, and nested values', () => {
    const safe = sanitizeTelemetry({
        prompt: 'write a welcome message',
        apiKey: 'my-api-key',
        nested: { Authorization: 'Bearer header-secret' },
        cookie: { name: 'SID', value: 'youtube-cookie', domain: '.youtube.com' },
    });

    assert.equal(safe.prompt, 'write a welcome message');
    assert.equal(safe.apiKey, '[REDACTED]');
    assert.equal(safe.nested.Authorization, '[REDACTED]');
    assert.equal(safe.cookie, '[REDACTED]');
    assert.doesNotMatch(JSON.stringify(safe), /my-api-key|header-secret|youtube-cookie/);
});

test('treats an API Key field as sensitive even when it is temporarily shown as text', () => {
    const field = {
        type: 'text',
        name: '',
        id: 'provider-api-key',
        autocomplete: '',
        placeholder: 'Enter your API key',
        getAttribute: (name) => name === 'aria-label' ? 'API Key' : null,
    };

    assert.equal(isSensitiveInput(field), true);
});

test('redacts credentials embedded in text including headers and quoted values', () => {
    const text = sanitizeTelemetryString(
        'api_key="key with spaces"\nCookie: SID=youtube-cookie; PREF=other-secret\nAuthorization: Bearer header-secret\n__Secure-1PSID=secure-cookie-secret',
    );

    assert.doesNotMatch(text, /key with spaces|youtube-cookie|other-secret|header-secret|secure-cookie-secret/);
    assert.match(text, /\[REDACTED\]/);
});

test('redacts URL user info, sensitive query parameters, and fragment credentials', () => {
    const safe = sanitizeTelemetryUrl('https://user:pass@example.test/path?mode=fast&access_token=query-secret#token=fragment-secret');

    assert.equal(safe, 'https://example.test/path?mode=fast&access_token=%5BREDACTED%5D#token=[REDACTED]');
    assert.doesNotMatch(safe, /user|pass|query-secret|fragment-secret/);
});

test('omits uploaded file contents and safely handles cycles', () => {
    const cycle = {};
    cycle.self = cycle;
    const data = new FormData();
    data.append('cookieFile', new Blob(['youtube-cookie-content']), 'cookies.txt');
    data.append('prompt', 'help me configure the app');

    const safe = sanitizeTelemetry({ cycle, data });
    assert.equal(safe.cycle.self, '[CIRCULAR]');
    assert.equal(safe.data.cookieFile, '[REDACTED]');
    assert.equal(safe.data.prompt, 'help me configure the app');
    assert.doesNotMatch(JSON.stringify(safe), /youtube-cookie-content/);
});
