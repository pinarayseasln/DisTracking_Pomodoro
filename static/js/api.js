// Shared JSON POST helper used by the Pomodoro session controls.
export async function apiPost(url, payload, keepalive = false) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive
    });
    const data = await response.json();
    if (!response.ok) {
        throw Object.assign(new Error(data.error || "Timer request failed."), { data });
    }
    return data;
}
