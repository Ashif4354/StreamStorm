# StreamStorm Socket.IO Events Documentation

This document describes all Socket.IO events emitted by the StreamStorm backend that the UI should listen to and handle.

## Overview

All events are emitted to the `streamstorm` room. The UI should join this room to receive these events.

---

## Events List

### 1. `system_metrics`

**Emitted By:** `SystemInfoEmitter.py`  
**Frequency:** Every 5 seconds  
**Purpose:** Provides real-time system metrics (CPU, RAM usage)

**Schema:**
```typescript
{
  cpu_percent: string,        // Current CPU usage percentage (e.g., "45.2")
  ram_percent: string,        // Current RAM usage percentage (e.g., "67.5")
  used_ram_gb: string,            // Used RAM in GB (e.g., "8.5")
  free_ram_percent: string,  // Free RAM percentage (e.g., "32.5")
  free_ram_gb: string,       // Free RAM in GB (e.g., "4.2")
  free_ram_mb: string        // Free RAM in MB (e.g., "4200")
}
```

**UI Action:**
- Update system metrics dashboard
- Display CPU and RAM usage charts/indicators

---

### 2. `log`

**Emitted By:** `CustomLogger.py` (SocketIOHandler)  
**Frequency:** Real-time (whenever a log message is generated)  
**Purpose:** Streams application logs to the UI in real-time

**Schema:**
```typescript
{
  message: string,  // The log message
  level: string,    // Log level: "INFO", "WARNING", "ERROR", "CRITICAL" (DEBUG is excluded)
  time: string      // Timestamp in HH:MM:SS format (e.g., "14:35:22")
}
```

**UI Action:**
- Display logs in a console/log viewer
- Color-code messages based on log level
- Auto-scroll to latest log entries

---

### 3. `instance_status`

**Emitted By:** `StreamStorm.py`  
**Frequency:** When instance status changes  
**Purpose:** Reports the status of individual storm instances (channels)

**Schema:**
```typescript
{
  instance: number,  // Channel index (e.g., 1, 2, 3...)
  status: string     // Status code (see below)
}
```

**Status Codes:**
- `"-1"` - **Idle** - Instance is idle (not storming)
- `"0"` - **Dead** - Instance has failed or been stopped by application
- `"1"` - **Getting Ready** - Instance is initializing and logging in
- `"2"` - **Ready** - Instance is ready to start storming (waiting for all instances)
- `"3"` - **Storming** - Instance is actively sending messages

**UI Action:**
- Update instance/channel status indicators
- Show visual feedback (colors, icons) for each instance state
- Display total ready/active/dead instances count

---

### 4. `total_messages`

**Emitted By:** `StreamStorm.py` (messages_handler)  
**Frequency:** Every 5 seconds  
**Purpose:** Reports the total number of messages sent since storm started

**Schema:**
```typescript
{
  total_messages: number  // Cumulative message count (e.g., 1543)
}
```

**UI Action:**
- Display total messages counter
- Update metrics dashboard

---

### 5. `messages_rate`

**Emitted By:** `StreamStorm.py` (messages_handler)  
**Frequency:** Every 5 seconds  
**Purpose:** Reports the current message sending rate

**Schema:**
```typescript
{
  message_rate: number  // Messages per minute (e.g., 120.5)
}
```

**UI Action:**
- Display current message rate (messages/minute)
- Show rate trends or graphs
- Update performance metrics

---

### 6. `storm_stopped`

**Emitted By:**
- `StormRouter.py` (when manually stopped via API)
- `StormStopper.py` (when all instances die automatically)

**Frequency:** Once when storm stops  
**Purpose:** Notifies UI that the storm has ended

**Schema:**
```typescript
// No payload - simple event notification
```

**UI Action:**
- Reset storm UI to initial state
- Clear instance statuses
- Show "Storm Stopped" notification
- Re-enable "Start Storm" button
- Disable "Stop/Pause/Resume" buttons

---

### 7. `storm_paused`

**Emitted By:** `StormRouter.py`  
**Frequency:** Once when storm is paused  
**Purpose:** Notifies UI that the storm has been paused

**Schema:**
```typescript
// No payload - simple event notification
```

**UI Action:**
- Update UI to show "Paused" state
- Change button states (disable Pause, enable Resume)
- Show pause indicator on dashboard
- Optionally pause message rate updates

---

### 8. `storm_resumed`

**Emitted By:** `StormRouter.py`  
**Frequency:** Once when storm is resumed  
**Purpose:** Notifies UI that the storm has been resumed

**Schema:**
```typescript
// No payload - simple event notification
```

**UI Action:**
- Update UI to show "Active" state
- Change button states (enable Pause, disable Resume)
- Remove pause indicator
- Resume normal operation display

---

## Connection Setup

### Client-Side Implementation Example

```typescript
import { io } from 'socket.io-client';

// Connect to the Socket.IO server
const socket = io('http://localhost:8000', {
  transports: ['websocket']
});

// Join the streamstorm room
socket.emit('join', 'streamstorm');

// Listen to all events
socket.on('system_metrics', (data) => {
  console.log('System Info:', data);
  // Update system metrics UI
});

socket.on('log', (data) => {
  console.log(`[${data.time}] [${data.level}] ${data.message}`);
  // Add to log viewer
});

socket.on('instance_status', (data) => {
  console.log(`Instance ${data.instance}: ${data.status}`);
  // Update instance status UI
});

socket.on('total_messages', (data) => {
  console.log('Total Messages:', data.total_messages);
  // Update message counter
});

socket.on('messages_rate', (data) => {
  console.log('Message Rate:', data.message_rate);
  // Update rate display
});

socket.on('storm_stopped', () => {
  console.log('Storm Stopped');
  // Reset UI state
});

socket.on('storm_paused', () => {
  console.log('Storm Paused');
  // Show paused state
});

socket.on('storm_resumed', () => {
  console.log('Storm Resumed');
  // Show active state
});
```

---

## Event Flow Diagram

```
Storm Lifecycle:
1. User starts storm
2. instance_status: "0" (Getting Ready) - emitted for each instance
3. instance_status: "1" (Ready) - emitted when instance is ready
4. instance_status: "2" (Storming) - emitted when all instances start
5. total_messages & messages_rate - continuous updates every 5s
6. system_metrics - continuous updates every 5s
7. log - continuous real-time logs
8. storm_paused (optional) - if user pauses
9. storm_resumed (optional) - if user resumes
10. instance_status: "-1" (Dead) - if instance fails
11. storm_stopped - when all instances die or manually stopped
```

---

## Notes

- All events use the `streamstorm` room for broadcasting
- Events are emitted asynchronously using `await sio.emit()`
- The UI should handle connection failures and reconnection gracefully
- Some events (like `log` and `system_metrics`) emit continuously and may generate high traffic
- Consider implementing UI throttling or debouncing for high-frequency events

---

## Source Files

Event emissions can be found in:
- [`SystemInfoEmitter.py`](file:///d:/PROGRAMMING/PROJECTS/StreamStorm/src/Engine/StreamStorm/utils/SystemInfoEmitter.py) - `system_metrics`
- [`CustomLogger.py`](file:///d:/PROGRAMMING/PROJECTS/StreamStorm/src/Engine/StreamStorm/utils/CustomLogger.py) - `log`
- [`StreamStorm.py`](file:///d:/PROGRAMMING/PROJECTS/StreamStorm/src/Engine/StreamStorm/core/StreamStorm.py) - `instance_status`, `total_messages`, `messages_rate`
- [`StormRouter.py`](file:///d:/PROGRAMMING/PROJECTS/StreamStorm/src/Engine/StreamStorm/api/routers/StormRouter.py) - `storm_stopped`, `storm_paused`, `storm_resumed`
- [`StormStopper.py`](file:///d:/PROGRAMMING/PROJECTS/StreamStorm/src/Engine/StreamStorm/utils/StormStopper.py) - `storm_stopped`
