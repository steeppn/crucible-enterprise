# Era's Frontend Guide — CRUCIBLE Enterprise

> **For:** Era (Creative Lead)
> **Timeline:** Days 1-3 (June 10-12)
> **Goal:** Build 4 screens using AI tools — no coding experience needed

---

## What You're Building

CRUCIBLE has 4 screens. Think of them like pages in a web app:

| Screen | What It Does | Priority |
|---|---|---|
| **Home** | Employee picks their certification and starts a session | Build first |
| **Session** | Live conversation — questions appear, answers are typed or spoken | Most important |
| **Report** | Results page — readiness score, strengths, gaps, citations | Build second |
| **Dashboard** | Manager view — whole team's readiness at a glance | Build last |

---

## How to Build With AI

You don't need to write code from scratch. You'll use an AI tool to generate it for you. Here are your options:

| Tool | Best For | Link |
|---|---|---|
| **ChatGPT** (free) | Generating code you paste into files | chatgpt.com |
| **Claude** (free) | Great at clean, well-structured code | claude.ai |
| **Cursor** (free tier) | AI code editor — writes code directly into files | cursor.com |
| **v0.dev** (free) | Generates UI from text prompts, gives you copy-paste code | v0.dev |

**Recommended workflow:** Use ChatGPT or Claude to generate code, then paste it into files. If you use Cursor, it writes directly into your files.

---

## Step 1: Set Up Your Project Folder

Create a folder called `frontend` inside the `crucible-enterprise` project. Inside it, create these files:

```
frontend/
├── index.html          ← Home screen
├── session.html        ← Live conversation screen
├── report.html         ← Results screen
├── dashboard.html      ← Manager view
├── css/
│   └── style.css       ← Shared styles for all screens
└── js/
    └── app.js          ← Shared JavaScript logic
```

**How to do this:**
1. Open File Explorer
2. Go to `C:\Users\steph\Documents\crucible-enterprise`
3. Right-click → New → Folder → name it `frontend`
4. Inside `frontend`, create the files listed above (right-click → New → Text Document, then rename to `.html`, `.css`, or `.js`)

---

## Step 2: Build Each Screen

### Screen 1: Home Page (`index.html`)

**What it shows:**
- CRUCIBLE logo/title at the top
- A short tagline: "You don't know it until you can defend it."
- A dropdown to pick a certification (AZ-900, AZ-104, AZ-204, AZ-400, AZ-700)
- A text input for employee ID (placeholder: "L-1001")
- A "Start Session" button
- Dark theme, clean and modern

**Copy-paste this prompt into your AI tool:**

```
Build me a single HTML page for a certification readiness app called CRUCIBLE. The page should have:

- A header with the title "CRUCIBLE Enterprise" and a subtitle "You don't know it until you can defend it."
- A centered card with:
  - A dropdown labeled "Select Certification" with options: AZ-900 (Azure Fundamentals), AZ-104 (Azure Administrator), AZ-204 (Azure Developer), AZ-400 (Azure DevOps Engineer), AZ-700 (Azure Network Engineer)
  - A text input labeled "Employee ID" with placeholder "L-1001"
  - A large "Start Session" button
- A footer with "Built by Steph & Era | Microsoft Foundry Hackathon"
- Dark theme with a dark background (#0f0f0f), blue accent color (#4a9eff), rounded corners on cards and inputs, clean sans-serif font
- All CSS should be inline in a <style> tag in the same file
- No frameworks, just HTML, CSS, and vanilla JavaScript
- Make it responsive for desktop and mobile
- When the button is clicked, show an alert with the selected cert and employee ID (this is just for testing)
```

---

### Screen 2: Session Page (`session.html`)

**What it shows:**
- A chat-like conversation view
- Messages appear one by one with sender labels ("Examiner", "You", "Devil's Advocate")
- A text input at the bottom for typing answers
- A "Send" button
- Messages should fade in with a slight delay (simulating real-time)
- Each message shows the agent name, the message text, and any citations

**Copy-paste this prompt into your AI tool:**

```
Build me a single HTML page for a live conversation screen. This is for a certification assessment app where AI agents ask questions and the user answers.

The page should have:
- A header showing "Session: AZ-104 | Employee: L-1001" and a small "End Session" button
- A main chat area that takes up most of the screen, with messages displayed as bubbles:
  - Examiner messages on the left, blue background
  - User messages on the right, green background
  - Devil's Advocate messages on the left, orange/amber background
  - Each message shows the sender name in small text above the bubble, and the message text inside
  - Some messages should show a "Citations" line below in small gray text like "Source: AZ-104 Guide, Section 3.2"
- A bottom bar with a text input (placeholder: "Type your answer...") and a "Send" button
- Dark theme (#0f0f0f background, #1a1a2e card backgrounds, #4a9eff blue, #00d68f green, #f5a623 orange)
- All CSS inline in a <style> tag
- No frameworks

For JavaScript, simulate a live conversation with these messages appearing one every 2.5 seconds:

1. Examiner: "What is the difference between a Network Security Group and an Application Security Group in Azure?" (Citation: AZ-104 Guide, Section 3.2)
2. User: "NSGs filter traffic at the subnet or VM level, while ASGs are used to group VMs for easier rule management."
3. Devil's Advocate: "That's correct, but can you explain when you would use one over the other in a real deployment?" (Citation: AZ-104 Guide, Section 3.4)
4. Examiner: "How would you configure an NSG to allow HTTPS traffic to a specific subnet?" (Citation: AZ-104 Guide, Section 5.1)
5. User: "I'd create an inbound rule allowing TCP port 443 from any source to the destination subnet."
6. Devil's Advocate: "What about source IP restrictions? Would you allow traffic from anywhere in production?" (Citation: AZ-104 Guide, Section 5.3)

Each message should fade in with a smooth animation. When the user types in the input and presses Enter or clicks Send, their message should appear in the chat. After the simulated messages finish, show a "Session Complete — Generating Report..." message.
```

---

### Screen 3: Report Page (`report.html`)

**What it shows:**
- A big readiness score (e.g., "72%") with a circular progress indicator
- A list of strengths with green checkmarks
- A list of gaps with yellow warning icons
- Citations showing which knowledge base sections were referenced
- A "Back to Home" button

**Copy-paste this prompt into your AI tool:**

```
Build me a single HTML page for a certification readiness report. This shows the results after an employee completes a spoken assessment session.

The page should have:
- A header: "Assessment Report — AZ-104"
- A large circular progress indicator showing "72%" readiness score in the center, with a blue ring that fills to 72%
- Below the score, a summary line: "Moderate Readiness — Recommended: 2 more study sessions"
- Two columns side by side:
  - Left column "Strengths" with green checkmark icons:
    - Network Security Groups (Score: 85%)
    - Identity & Access Management (Score: 78%)
    - Virtual Networks (Score: 72%)
  - Right column "Areas to Improve" with yellow warning icons:
    - Storage Account Configuration (Score: 45%)
    - Azure Monitor & Diagnostics (Score: 38%)
    - ARM Templates (Score: 52%)
- A "Citations" section below showing:
  - "AZ-104 Guide, Section 3.2 — Network Security"
  - "AZ-104 Guide, Section 5.1 — Access Control"
  - "Microsoft Learn — NSG Best Practices"
- A "Back to Home" button at the bottom
- Dark theme matching the other screens (#0f0f0f background, #1a1a2e cards, #4a9eff blue, #00d68f green, #f5a623 orange)
- All CSS inline in a <style> tag
- No frameworks
- Make the circular progress indicator animate on page load (the ring should fill from 0 to 72% over 1.5 seconds)
```

---

### Screen 4: Dashboard Page (`dashboard.html`)

**What it shows:**
- A manager's view of the whole team
- A table or cards showing team members and their readiness scores
- A simple bar chart or color-coded grid showing readiness by certification
- Summary stats at the top: total learners, average readiness, certifications in progress

**Copy-paste this prompt into your AI tool:**

```
Build me a single HTML page for a team readiness dashboard. This is a manager's view showing how their team is progressing on certification readiness.

The page should have:
- A header: "Team Dashboard — Azure Certifications"
- Three summary cards at the top in a row:
  - "Total Learners: 8"
  - "Average Readiness: 64%"
  - "Certifications In Progress: 12"
- A table below showing team members:
  - Columns: Employee ID, Certification, Readiness Score (as a colored bar), Last Session, Status
  - Use this mock data:
    - L-1001, AZ-104, 72%, 2026-06-10, In Progress
    - L-1002, AZ-900, 88%, 2026-06-09, Ready
    - L-1003, AZ-204, 45%, 2026-06-08, Needs Study
    - L-1004, AZ-400, 61%, 2026-06-10, In Progress
    - L-1005, AZ-104, 79%, 2026-06-09, In Progress
    - L-1006, AZ-700, 33%, 2026-06-07, Needs Study
    - L-1007, AZ-900, 91%, 2026-06-10, Ready
    - L-1008, AZ-204, 55%, 2026-06-08, In Progress
  - Color code the readiness bars: green for 70%+, yellow for 40-69%, red for below 40%
- A simple bar chart below the table showing average readiness per certification (AZ-900: 89%, AZ-104: 75%, AZ-204: 50%, AZ-400: 61%, AZ-700: 33%)
  - You can use simple HTML/CSS bars, no chart library needed
- Dark theme matching the other screens
- All CSS inline in a <style> tag
- No frameworks
```

---

## Step 3: Shared Styling (`css/style.css`)

Once you have all 4 screens, you'll notice they each have their own inline styles. Let's extract the shared styles into one file.

**Copy-paste this prompt:**

```
I have 4 HTML pages that each have their own inline <style> tags. I want to extract all the shared styles into a single CSS file called style.css.

Here are the common styles I need:
- Body: dark background (#0f0f0f), white text, sans-serif font (Inter or system-ui)
- Header: centered, large title, smaller subtitle, padding
- Cards: dark background (#1a1a2e), rounded corners (12px), padding, subtle border
- Buttons: blue background (#4a9eff), white text, rounded corners, hover effect (slightly lighter blue)
- Inputs: dark background (#2a2a3e), light border, rounded corners, white text, focus state with blue border
- Chat bubbles: left-aligned (blue) and right-aligned (green), rounded corners, padding
- Tables: dark rows, alternating row colors, hover highlight
- Progress bars: colored fill (green for good, yellow for medium, red for low)
- Animations: fade-in for messages, smooth transitions on hover

Create a clean, well-organized CSS file with comments separating each section. Use CSS custom properties (variables) for colors so they're easy to change later.
```

Then in each HTML file, replace the inline `<style>` tag with:
```html
<link rel="stylesheet" href="css/style.css">
```

---

## Step 4: Shared JavaScript (`js/app.js`)

**Copy-paste this prompt:**

```
Create a JavaScript file called app.js with these utility functions for a certification readiness app:

1. `navigateTo(page)` — navigates to another HTML page (e.g., navigateTo('session.html'))
2. `showLoading(elementId)` — shows a loading spinner in the given element
3. `hideLoading(elementId)` — hides the loading spinner
4. `formatDate(dateString)` — formats a date like "2026-06-10" into "June 10, 2026"
5. `getScoreColor(score)` — returns 'green' for 70+, 'yellow' for 40-69, 'red' for below 40
6. `animateProgress(element, targetPercent, duration)` — animates a circular progress indicator from 0 to targetPercent over the given duration in milliseconds

Include comments explaining what each function does. Use vanilla JavaScript only, no frameworks.
```

Then in each HTML file, add before the closing `</body>` tag:
```html
<script src="js/app.js"></script>
```

---

## Step 5: Make the Session Screen Interactive

The session screen needs to feel alive. Here's how to make it work:

**Copy-paste this prompt:**

```
I have a session.html page with a chat interface. I need to add real-time message streaming that simulates a WebSocket connection.

Add this JavaScript functionality:
1. When the page loads, start a simulated message stream
2. Messages come from a predefined array with these properties: { sender, text, citation, delay }
3. Each message appears with a fade-in animation after its delay
4. When the user types in the input and presses Enter, their message appears immediately
5. After the user sends a message, show a "Thinking..." indicator for 1.5 seconds, then show the next agent message
6. When all messages are done, show "Session Complete — Generating Report..." with a button to go to the report page

Use smooth animations and make it feel like a real live conversation. The "Thinking..." indicator should be three animated dots that pulse.
```

---

## Step 6: Add Navigation Between Screens

Make the buttons actually navigate between pages.

**Copy-paste this prompt:**

```
Add navigation to my CRUCIBLE Enterprise frontend:

1. On index.html (Home): When "Start Session" is clicked, save the selected cert and employee ID to localStorage, then navigate to session.html
2. On session.html: Read the cert and employee ID from localStorage and display them in the header. When "End Session" is clicked, navigate to report.html
3. On report.html: Read the cert from localStorage and display it in the header. When "Back to Home" is clicked, navigate to index.html
4. On dashboard.html: Add a "Back to Home" button that navigates to index.html

Use window.location.href for navigation and localStorage for passing data between pages.
```

---

## What the Data Will Look Like When Backend Is Ready

Right now you're using fake data. When Steph finishes the backend, the screens will connect to real data. Here's what the real data will look like — you don't need to change your UI, just swap the source.

### Starting a Session
**You send:**
```json
{ "employee_id": "L-1001", "cert_id": "AZ-104" }
```
**You get back:**
```json
{ "session_id": "abc-123", "status": "started" }
```

### Live Messages (WebSocket)
```json
{
  "type": "question",
  "agent": "Examiner",
  "content": "What is Azure RBAC?",
  "citations": ["AZ-104 Guide, Section 3.2"]
}
```

### Final Report
```json
{
  "readiness_score": 72,
  "strengths": [
    { "topic": "Network Security", "score": 85 },
    { "topic": "Identity Management", "score": 78 }
  ],
  "gaps": [
    { "topic": "Storage Accounts", "score": 45 },
    { "topic": "Monitoring", "score": 38 }
  ],
  "citations": ["AZ-104 Guide, Section 5.1", "AZ-104 Guide, Section 7.3"]
}
```

### Dashboard
```json
{
  "total_learners": 8,
  "average_readiness": 64,
  "learners": [
    { "id": "L-1001", "cert": "AZ-104", "score": 72, "last_session": "2026-06-10", "status": "In Progress" }
  ]
}
```

**When the backend is ready, Steph will give you the exact code to connect these. Your UI won't need to change — just the data source.**

---

## Day-by-Day Timeline

| Day | Date | What to Build |
|---|---|---|
| **Day 1** | June 10 | Home screen (`index.html`) + basic shared CSS |
| **Day 2** | June 11 | Session screen (`session.html`) + Report screen (`report.html`) |
| **Day 3** | June 12 | Dashboard screen (`dashboard.html`) + navigation between all screens + shared JS |

**Each day:** Pick the prompt for that screen, paste it into your AI tool, copy the output into the right file, open it in your browser to check it looks good.

---

## Quick Troubleshooting

| Problem | Fix |
|---|---|
| Page looks broken | Check that all HTML tags are closed properly (`</div>`, `</style>`, etc.) |
| Styles not applying | Make sure the `<link>` to `style.css` has the correct path |
| JavaScript not working | Open browser DevTools (F12) → Console tab → look for red error messages |
| Messages not appearing | Check that the `<script>` tag is at the bottom of the HTML, before `</body>` |
| Navigation not working | Make sure the file names match exactly (`session.html` not `Session.html`) |

---

## When You're Stuck

1. Paste the error message or describe what's not working into your AI tool
2. Include the relevant code (the HTML or JS section that's causing the issue)
3. Ask: "This isn't working. Here's my code: [paste code]. The error is: [paste error]. How do I fix it?"

---

## Final Checklist

Before Day 3 ends, make sure:

- [ ] All 4 HTML files exist and open in a browser
- [ ] Home screen lets you pick a cert and enter an ID
- [ ] Session screen shows a simulated conversation with messages appearing over time
- [ ] Report screen shows a readiness score, strengths, and gaps
- [ ] Dashboard screen shows a team table with color-coded scores
- [ ] Buttons navigate between screens
- [ ] All screens share the same dark theme and styling
- [ ] Everything works on both desktop and mobile (resize your browser to test)
