# Redux Toolkit architecture

## Store

`frontend/src/store/index.js` configures one Redux store and `frontend/src/main.jsx`
wraps the existing application with `Provider`. Redux DevTools are enabled in
development. No access token, password, or secret is stored in Redux; authentication
credentials remain in the existing browser storage/API mechanism.

## Six slices

| Slice | State and actions | Current integration |
|---|---|---|
| `auth` | `sessionSet`, `loggedOut`, `restoreSession`, `loginSession` | App session restoration, login callback, logout and unauthorized handling |
| `jobs` | listings, filters, loading/error; `loadJobs`, `filtersChanged` | Jobs page search requests dispatch `loadJobs` |
| `applications` | student rows, status filter, updates; `loadApplications` | Jobs and Saved & applications pages dispatch application loading |
| `events` | event rows and registrations; `loadEvents`, `registrationAdded` | Events page dispatches event listing loading |
| `saved` | saved jobs/events and loading/error; `loadSavedItems`, `itemAdded`, `itemRemoved` | Jobs, Events, and Saved pages dispatch saved-item loading |
| `assistant` | ordered messages, conversation ID, metrics, pending save, status/error; `sendAssistantMessage`, `conversationStarted`, `confirmationResolved` | Assistant page uses Redux state and actions, including navigation persistence |

Async thunks reuse the existing `services/api.js` contract. Backend authorization,
confirmation, and response shapes are unchanged. Some legacy pages retain local
presentation state for modals and form controls; server-backed fetches are dispatched
through the slices so the store is part of the real workflow rather than a screenshot
fixture.

## Persistence

The Provider is mounted above the router, so navigating between routes does not reset
Redux conversation state. The backend already persists conversations in Mongo when
available. Redux state is not claimed to survive a full browser refresh; refresh
hydration still depends on the existing authenticated session and assistant API
conversation ID behavior.

## DevTools evidence procedure

1. Start the frontend with `npm run dev`.
2. Open Redux DevTools in the browser and select the CareerBridge store.
3. Log in and inspect `auth/sessionSet` and the `auth` state.
4. Open Assistant and send a suggestion; inspect `assistant/sendAssistantMessage/pending`
   and `/fulfilled`, including ordered messages and metrics.
5. Open Jobs or Saved & applications and inspect the corresponding thunk and slice.

No DevTools screenshot was fabricated or captured in this batch; the procedure is
ready for the required live evidence capture.
